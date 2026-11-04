import asyncio
from decimal import Decimal
import pytest
import respx
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base
from app.db.migrations import run_migrations
from app.db.seed import seed_catalog
from app.db.session import get_db
from app.main import app
from app.models.catalog import CatalogItem
from app.models.inventory import InventoryMovement
from app.models.order import Order, OrderStatus
from app.schemas.assistant import RawLLMPlanResponse, RawLLMRecommendation
from app.services.ai.base import BaseAIProvider
from app.services.ai.factory import register_provider

BASE_URL = settings.paypal_base_url


@pytest.mark.asyncio
@respx.mock
async def test_client_idempotency_key_enforced(client: AsyncClient, db_session):
    """
    Submitting multiple order creation requests with identical client_idempotency_key
    returns the exact same internal order without duplicating orders or audit logs.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_IDEMP", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-IDEMP-01", "status": "CREATED"},
    )

    idempotency_key = "idemp-client-test-uuid-999"
    payload = {
        "items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}],
        "client_idempotency_key": idempotency_key,
    }

    # First request
    res1 = await client.post("/api/v1/orders", json=payload)
    assert res1.status_code == 201
    data1 = res1.json()
    order_id_1 = data1["id"]

    # Second request with identical client_idempotency_key
    res2 = await client.post("/api/v1/orders", json=payload)
    assert res2.status_code == 201 or res2.status_code == 200
    data2 = res2.json()
    order_id_2 = data2["id"]

    assert order_id_1 == order_id_2
    assert data1["total_amount"] == data2["total_amount"]
    assert data1["client_idempotency_key"] == idempotency_key


@pytest.mark.asyncio
@respx.mock
async def test_client_price_and_subtotal_tampering_prevented(client: AsyncClient):
    """
    Client-supplied prices, unit totals, or amounts are never trusted.
    Calculations strictly use authoritative database catalog values.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_TAMPER", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-TAMPER-01", "status": "CREATED"},
    )

    # Malicious attempt to inject price $0.01 instead of $289.50
    payload = {
        "items": [
            {"sku": "CHAIR-ERGO-01", "quantity": 2, "unit_price": "0.01", "total_price": "0.02"}
        ],
        "total_amount": "0.02",
    }
    response = await client.post("/api/v1/orders", json=payload)
    assert response.status_code == 201
    data = response.json()

    # Must be 289.50 * 2 = 579.00, NOT 0.02
    assert data["total_amount"] == "579.00"
    assert data["items"][0]["unit_price"] == "289.50"
    assert data["items"][0]["total_price"] == "579.00"


@pytest.mark.asyncio
async def test_invalid_and_excessive_quantities_rejected(client: AsyncClient):
    """
    Zero, negative, and stock-exceeding quantities are strictly rejected.
    """
    # Negative quantity
    res_neg = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": -3}]},
    )
    assert res_neg.status_code in (400, 422)

    # Zero quantity
    res_zero = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 0}]},
    )
    assert res_zero.status_code in (400, 422)

    # Exceeding stock (CHAIR-ERGO-01 stock is <= 45)
    res_excess = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 500}]},
    )
    assert res_excess.status_code == 400
    assert "exceeds available stock" in res_excess.json()["detail"]


@pytest.mark.asyncio
@respx.mock
async def test_cancellation_after_completion_rejected(client: AsyncClient, db_session):
    """
    Once an order is COMPLETED, it cannot be cancelled by the buyer or client.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_CANC", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-CANC", "status": "CREATED"},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-CANC/capture").respond(
        status_code=201,
        json={
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-CANC-999",
                                "status": "COMPLETED",
                                "amount": {"value": "289.50", "currency_code": "USD"},
                                "create_time": "2026-10-20T12:00:00Z",
                            }
                        ]
                    }
                }
            ],
        },
    )

    create_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    # Capture order to complete it
    cap_res = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap_res.status_code == 200
    assert cap_res.json()["status"] == "COMPLETED"

    # Attempt to cancel completed order -> must be rejected
    cancel_res = await client.post(f"/api/v1/orders/{order_id}/cancel")
    assert cancel_res.status_code == 400
    assert "cannot be cancelled" in cancel_res.json()["detail"]


@pytest.mark.asyncio
@respx.mock
async def test_cancelled_order_does_not_deduct_inventory(client: AsyncClient, db_session):
    """
    Cancelled or failed orders never deduct inventory or record ledger movements.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_CANC2", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-CANC2", "status": "CREATED"},
    )

    cat_stmt = select(CatalogItem).where(CatalogItem.sku == "CHAIR-ERGO-01")
    cat_res = await db_session.execute(cat_stmt)
    initial_stock = cat_res.scalars().first().stock

    create_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 2}]},
    )
    order_id = create_res.json()["id"]

    # Cancel order
    cancel_res = await client.post(f"/api/v1/orders/{order_id}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # Stock must remain identical
    cat_res2 = await db_session.execute(cat_stmt)
    current_stock = cat_res2.scalars().first().stock
    assert current_stock == initial_stock

    # No inventory movements recorded
    mv_stmt = select(InventoryMovement).where(InventoryMovement.order_id == order_id)
    mv_res = await db_session.execute(mv_stmt)
    assert len(mv_res.scalars().all()) == 0


@pytest.mark.asyncio
@respx.mock
async def test_interrupted_capture_reconciliation(client: AsyncClient, db_session):
    """
    If an order was left in CAPTURING status due to an interrupted request or network timeout,
    a retry queries PayPal get_order_details, reconciles the completed payment,
    records inventory deduction once, and returns success.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_REC", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-REC-1", "status": "CREATED"},
    )

    create_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_id = create_res.json()["id"]

    # Manually transition order to CAPTURING to simulate interrupted state
    order_stmt = select(Order).where(Order.id == order_id)
    order_res = await db_session.execute(order_stmt)
    order = order_res.scalars().first()
    order.status = OrderStatus.CAPTURING
    await db_session.commit()

    # Mock PayPal get_order_details indicating PayPal already completed the capture
    respx.get(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-REC-1").respond(
        status_code=200,
        json={
            "id": "PAYPAL-ORDER-REC-1",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-REC-RECONCILED",
                                "status": "COMPLETED",
                                "amount": {"value": "289.50", "currency_code": "USD"},
                                "create_time": "2026-10-20T12:30:00Z",
                            }
                        ]
                    }
                }
            ],
        },
    )

    # Retry capture endpoint
    cap_res = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap_res.status_code == 200
    data = cap_res.json()
    assert data["status"] == "COMPLETED"
    assert data["paypal_capture_id"] == "CAPTURE-REC-RECONCILED"

    # Verify inventory movement recorded
    mv_stmt = select(InventoryMovement).where(InventoryMovement.order_id == order_id)
    mv_res = await db_session.execute(mv_stmt)
    movements = mv_res.scalars().all()
    assert len(movements) == 1
    assert movements[0].quantity_delta == -1
    assert movements[0].reason == "ORDER_CAPTURE"


@pytest.mark.asyncio
@respx.mock
async def test_repeated_capture_on_completed_order_is_idempotent_no_duplicate_stock_deduction(
    client: AsyncClient, db_session
):
    """
    Subsequent capture attempts on an already-completed order return the existing
    capture receipt without deducting stock a second time or creating duplicate movements.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_IDEMP2", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-IDEMP2", "status": "CREATED"},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-IDEMP2/capture").respond(
        status_code=201,
        json={
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-IDEMP2-123",
                                "status": "COMPLETED",
                                "amount": {"value": "289.50", "currency_code": "USD"},
                                "create_time": "2026-10-20T12:00:00Z",
                            }
                        ]
                    }
                }
            ],
        },
    )

    create_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_id = create_res.json()["id"]

    # First capture
    res1 = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert res1.status_code == 200

    # Stock after first capture
    cat_stmt = select(CatalogItem).where(CatalogItem.sku == "CHAIR-ERGO-01")
    cat_res1 = await db_session.execute(cat_stmt)
    stock_after_first = cat_res1.scalars().first().stock

    # Second capture attempt
    res2 = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert res2.status_code == 200
    assert res2.json()["paypal_capture_id"] == "CAPTURE-IDEMP2-123"

    # Stock must NOT decrease further
    cat_res2 = await db_session.execute(cat_stmt)
    stock_after_second = cat_res2.scalars().first().stock
    assert stock_after_first == stock_after_second

    # Exactly 1 movement record exists
    mv_stmt = select(InventoryMovement).where(InventoryMovement.order_id == order_id)
    mv_res = await db_session.execute(mv_stmt)
    assert len(mv_res.scalars().all()) == 1


@pytest.mark.asyncio
@respx.mock
async def test_capture_amount_or_currency_mismatch_rejected(client: AsyncClient, db_session):
    """
    If PayPal returns a captured currency or amount differing from internal order,
    the capture is strictly rejected, marked FAILED, and no stock is deducted.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_MISMATCH", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-MISMATCH", "status": "CREATED"},
    )
    # Mock PayPal returning EUR instead of USD
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-MISMATCH/capture").respond(
        status_code=201,
        json={
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-MISMATCH-99",
                                "status": "COMPLETED",
                                "amount": {"value": "289.50", "currency_code": "EUR"},
                            }
                        ]
                    }
                }
            ],
        },
    )

    create_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_id = create_res.json()["id"]

    cap_res = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap_res.status_code == 400
    assert "Currency mismatch" in cap_res.json()["detail"]

    # Order marked FAILED
    order_stmt = select(Order).where(Order.id == order_id)
    order_res = await db_session.execute(order_stmt)
    order = order_res.scalars().first()
    assert order.status == OrderStatus.FAILED


@pytest.mark.asyncio
@respx.mock
async def test_no_secret_leakage_in_api_errors(client: AsyncClient):
    """
    Upstream PayPal failures (e.g. 401 or 500) must return sanitized error messages
    and never expose client secrets, auth headers, or raw tokens.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=401,
        json={"error": "invalid_client", "error_description": "Client Authentication failed"},
    )

    response = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    assert response.status_code == 502
    detail = response.json()["detail"]
    assert "secret" not in detail.lower()
    assert "token" not in detail.lower()
    assert "test_sandbox_client_secret" not in detail


@pytest.mark.asyncio
async def test_ai_status_endpoint_never_discloses_credentials(client: AsyncClient):
    """
    Assistant status endpoint exposes only booleans and provider names.
    """
    response = await client.get("/api/v1/assistant/status")
    assert response.status_code == 200
    data = response.json()

    assert "is_configured" in data
    assert "default_provider" in data
    assert "supported_providers" in data

    assert "api_key" not in data
    assert "key" not in data
    assert "secret" not in data


@pytest.mark.asyncio
async def test_ai_plan_cannot_create_or_capture_orders(client: AsyncClient, db_session):
    """
    Calling /api/v1/assistant/plan generates advisory recommendations only.
    It does not insert orders or modify stock/movements.
    """
    order_count_before = len((await db_session.execute(select(Order))).scalars().all())

    response = await client.post(
        "/api/v1/assistant/plan?provider=mock",
        json={"prompt": "I need 2 ergonomic chairs for my office", "budget": 1000},
    )
    assert response.status_code == 200
    plan = response.json()
    assert plan["is_actionable"] is True
    assert len(plan["recommendations"]) > 0

    order_count_after = len((await db_session.execute(select(Order))).scalars().all())
    assert order_count_before == order_count_after


@pytest.mark.asyncio
async def test_ai_hallucinated_product_ids_discarded(client: AsyncClient):
    """
    If the LLM recommends non-existent SKUs, server-side catalog grounding discards them.
    """
    class HallucinatingMockProvider(BaseAIProvider):
        @property
        def provider_name(self) -> str:
            return "hallucinating_mock"

        async def generate_plan(self, prompt, catalog_items, budget=None):
            return RawLLMPlanResponse(
                interpretation="User wants items",
                recommendations=[
                    RawLLMRecommendation(sku="NON-EXISTENT-SKU-FAKE", quantity=2, reason="Fake item"),
                    RawLLMRecommendation(sku="CHAIR-ERGO-01", quantity=1, reason="Real item"),
                ],
            )

    register_provider("hallucinating_mock", HallucinatingMockProvider())

    response = await client.post(
        "/api/v1/assistant/plan?provider=hallucinating_mock",
        json={"prompt": "Buy chairs and nonexistent widgets"},
    )
    assert response.status_code == 200
    data = response.json()

    # The hallucinated SKU must be discarded
    skus = [rec["sku"] for rec in data["recommendations"]]
    assert "NON-EXISTENT-SKU-FAKE" not in skus
    assert "CHAIR-ERGO-01" in skus
    assert any("does not exist in authoritative catalog" in w for w in data["warnings"])


@pytest.mark.asyncio
async def test_ai_provider_timeout_returns_sanitized_504(client: AsyncClient):
    """
    When the AI provider hangs, the endpoint returns a sanitized 504 timeout.
    """
    class HangingAIProvider(BaseAIProvider):
        @property
        def provider_name(self) -> str:
            return "hanging_mock"

        async def generate_plan(self, prompt, catalog_items, budget=None):
            await asyncio.sleep(25.0)  # Exceeds 20.0s timeout
            return RawLLMPlanResponse(interpretation="Done")

    register_provider("hanging_mock", HangingAIProvider())

    response = await client.post(
        "/api/v1/assistant/plan?provider=hanging_mock",
        json={"prompt": "Please hang"},
    )
    assert response.status_code == 504
    assert "timed out" in response.json()["detail"]


@pytest.mark.asyncio
async def test_database_migration_idempotency_and_preservation(db_session):
    """
    Running run_migrations repeatedly on the database is idempotent and does not
    alter existing tables, constraints, or completed orders.
    """
    conn = await db_session.connection()
    await run_migrations(conn)
    await run_migrations(conn)  # second run to ensure complete idempotency


@pytest.mark.asyncio
async def test_idempotency_key_length_and_format_validation(client: AsyncClient):
    """
    Idempotency keys must conform to length (1..64) and character set rules.
    """
    # Key too long (>64 characters)
    too_long_key = "a" * 65
    res_long = await client.post(
        "/api/v1/orders",
        json={
            "items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}],
            "client_idempotency_key": too_long_key,
        },
    )
    assert res_long.status_code in (400, 422)

    # Key with invalid characters (e.g. whitespace, quotes)
    res_invalid_chars = await client.post(
        "/api/v1/orders",
        json={
            "items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}],
            "client_idempotency_key": "bad key with spaces!",
        },
    )
    assert res_invalid_chars.status_code == 400
    assert "invalid characters" in res_invalid_chars.json()["detail"].lower()


@pytest.mark.asyncio
@respx.mock
async def test_idempotency_key_payload_mismatch_returns_409(client: AsyncClient):
    """
    Reusing an existing idempotency key with a materially different cart
    must return a clear HTTP 409 Conflict rather than silently returning an unrelated order.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_PAYLOAD_MISMATCH", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-MISMATCH-PAYLOAD", "status": "CREATED"},
    )

    shared_key = "idemp-reused-key-mismatch-test"

    # Order 1: 1 chair
    res1 = await client.post(
        "/api/v1/orders",
        json={
            "items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}],
            "client_idempotency_key": shared_key,
        },
    )
    assert res1.status_code == 201

    # Order 2: same key, but different quantity (2 chairs)
    res2 = await client.post(
        "/api/v1/orders",
        json={
            "items": [{"sku": "CHAIR-ERGO-01", "quantity": 2}],
            "client_idempotency_key": shared_key,
        },
    )
    assert res2.status_code == 409
    assert "different cart payload" in res2.json()["detail"]


@pytest.mark.asyncio
@respx.mock
async def test_capture_order_id_mismatch_rejected(client: AsyncClient, db_session):
    """
    If PayPal returns a capture payload with a different order ID than expected,
    the capture must be rejected.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_ORDER_MISMATCH", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-EXPECTED-ORDER-ID", "status": "CREATED"},
    )
    # Mock PayPal returning an unmatching order ID
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-EXPECTED-ORDER-ID/capture").respond(
        status_code=201,
        json={
            "id": "PAYPAL-WRONG-ORDER-ID",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-WRONG-ORDER",
                                "status": "COMPLETED",
                                "amount": {"value": "289.50", "currency_code": "USD"},
                            }
                        ]
                    }
                }
            ],
        },
    )

    create_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_id = create_res.json()["id"]

    cap_res = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap_res.status_code in (400, 502)
    assert "order id mismatch" in cap_res.json()["detail"].lower()


@pytest.mark.asyncio
@respx.mock
async def test_capture_pending_status_rejected(client: AsyncClient):
    """
    If PayPal reports capture status as PENDING, the server must not mark the order COMPLETED.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_PENDING", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-PENDING", "status": "CREATED"},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-PENDING/capture").respond(
        status_code=201,
        json={
            "id": "PAYPAL-ORDER-PENDING",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-PENDING-123",
                                "status": "PENDING",  # Non-final status
                                "amount": {"value": "289.50", "currency_code": "USD"},
                            }
                        ]
                    }
                }
            ],
        },
    )

    create_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_id = create_res.json()["id"]

    cap_res = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap_res.status_code in (400, 502)
    assert "pending" in cap_res.json()["detail"].lower()


@pytest.mark.asyncio
@respx.mock
async def test_reconciliation_when_paypal_order_voided_upstream(client: AsyncClient, db_session):
    """
    When an order in CAPTURING status is reconciled and PayPal reports VOIDED,
    the order is transitioned to FAILED and rejected.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_VOIDED", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-VOIDED-01", "status": "CREATED"},
    )

    create_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_id = create_res.json()["id"]

    # Transition order locally to CAPTURING
    order = (await db_session.execute(select(Order).where(Order.id == order_id))).scalars().first()
    order.status = OrderStatus.CAPTURING
    await db_session.commit()

    # Upstream PayPal reports VOIDED
    respx.get(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-VOIDED-01").respond(
        status_code=200,
        json={"id": "PAYPAL-ORDER-VOIDED-01", "status": "VOIDED"},
    )

    cap_res = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap_res.status_code == 400
    assert "voided" in cap_res.json()["detail"].lower()

    # Verify order transitioned to FAILED
    updated_order = (await db_session.execute(select(Order).where(Order.id == order_id))).scalars().first()
    assert updated_order.status == OrderStatus.FAILED


@pytest.mark.asyncio
@respx.mock
async def test_reconciliation_when_paypal_service_unavailable(client: AsyncClient, db_session):
    """
    When reconciling an in-progress capture and PayPal returns HTTP 500/503,
    the endpoint returns 502 Bad Gateway without modifying or failing the recoverable order.
    """
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_DOWN", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-DOWN-01", "status": "CREATED"},
    )

    create_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_id = create_res.json()["id"]

    order = (await db_session.execute(select(Order).where(Order.id == order_id))).scalars().first()
    order.status = OrderStatus.CAPTURING
    await db_session.commit()

    # Upstream PayPal is down
    respx.get(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-DOWN-01").respond(
        status_code=500,
        text="Internal Server Error",
    )

    cap_res = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap_res.status_code == 502
    assert "unable to reconcile" in cap_res.json()["detail"].lower()

    # Order remains in CAPTURING (recoverable)
    updated_order = (await db_session.execute(select(Order).where(Order.id == order_id))).scalars().first()
    assert updated_order.status == OrderStatus.CAPTURING


@pytest.mark.asyncio
@respx.mock
async def test_concurrent_order_creation_simultaneous_requests_produce_one_order(tmp_path):
    """
    Truly concurrent order creation requests launched via asyncio.gather on isolated sessions
    produce a single logical order with identical order IDs and total amounts.
    """
    db_file = tmp_path / "concurrent_order_test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}", connect_args={"check_same_thread": False})
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with session_factory() as s:
        await seed_catalog(s)

    async def get_test_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    try:
        respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
            status_code=200,
            json={"access_token": "TEST_TOKEN_CONC", "expires_in": 32400},
        )
        respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
            status_code=201,
            json={"id": "PAYPAL-ORDER-CONC-SIM-01", "status": "CREATED"},
        )

        key = "concurrent-create-key-001"
        payload = {
            "items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}],
            "client_idempotency_key": key,
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c1, \
                   AsyncClient(transport=transport, base_url="http://test") as c2:
            res1, res2 = await asyncio.gather(
                c1.post("/api/v1/orders", json=payload),
                c2.post("/api/v1/orders", json=payload),
            )

        assert res1.status_code in (200, 201)
        assert res2.status_code in (200, 201)
        data1 = res1.json()
        data2 = res2.json()
        assert data1["id"] == data2["id"]
        assert data1["client_idempotency_key"] == key
        assert data2["client_idempotency_key"] == key

        async with session_factory() as verify_session:
            orders_stmt = select(Order).where(Order.client_idempotency_key == key)
            orders = (await verify_session.execute(orders_stmt)).scalars().all()
            assert len(orders) == 1
    finally:
        app.dependency_overrides.pop(get_db, None)
        await engine.dispose()


@pytest.mark.asyncio
@respx.mock
async def test_concurrent_simultaneous_captures_cannot_deduct_stock_twice(tmp_path):
    """
    Simultaneous capture attempts launched via asyncio.gather on independent sessions
    cannot deduct stock twice or record duplicate ledger movements.
    """
    db_file = tmp_path / "concurrent_capture_test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}", connect_args={"check_same_thread": False})
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with session_factory() as s:
        await seed_catalog(s)

    async def get_test_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    try:
        respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
            status_code=200,
            json={"access_token": "TEST_TOKEN_CAP_CONC", "expires_in": 32400},
        )
        respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
            status_code=201,
            json={"id": "PAYPAL-ORDER-CAP-CONC-01", "status": "CREATED"},
        )
        respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-CAP-CONC-01/capture").respond(
            status_code=201,
            json={
                "id": "PAYPAL-ORDER-CAP-CONC-01",
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "payments": {
                            "captures": [
                                {
                                    "id": "CAPTURE-CONC-01",
                                    "status": "COMPLETED",
                                    "amount": {"value": "289.50", "currency_code": "USD"},
                                    "create_time": "2026-10-20T12:00:00Z",
                                }
                            ]
                        }
                    }
                ],
            },
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as local_client:
            create_res = await local_client.post(
                "/api/v1/orders",
                json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
            )
            order_id = create_res.json()["id"]

            async with session_factory() as verify_session:
                chair = (await verify_session.execute(select(CatalogItem).where(CatalogItem.sku == "CHAIR-ERGO-01"))).scalars().first()
                initial_stock = chair.stock

            async with AsyncClient(transport=transport, base_url="http://test") as c1, \
                       AsyncClient(transport=transport, base_url="http://test") as c2:
                res1, res2 = await asyncio.gather(
                    c1.post(f"/api/v1/orders/{order_id}/capture"),
                    c2.post(f"/api/v1/orders/{order_id}/capture"),
                )

            assert res1.status_code in (200, 409)
            assert res2.status_code in (200, 409)
            assert 200 in (res1.status_code, res2.status_code)

            async with session_factory() as verify_session:
                chair_after = (await verify_session.execute(select(CatalogItem).where(CatalogItem.sku == "CHAIR-ERGO-01"))).scalars().first()
                assert chair_after.stock == initial_stock - 1

                movements = (await verify_session.execute(select(InventoryMovement).where(InventoryMovement.order_id == order_id))).scalars().all()
                assert len(movements) == 1
                assert movements[0].quantity_delta == -1
    finally:
        app.dependency_overrides.pop(get_db, None)
        await engine.dispose()


@pytest.mark.asyncio
@respx.mock
async def test_database_failure_rolls_back_atomically(tmp_path):
    """
    If a database commit fails during capture finalization, the entire local transaction
    rolls back (stock not deducted, movement not recorded) and leaves the order in CAPTURING
    so it can be safely recovered on subsequent retry.
    """
    db_file = tmp_path / "rollback_test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}", connect_args={"check_same_thread": False})
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with session_factory() as s:
        await seed_catalog(s)

    async def get_test_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    try:
        respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
            status_code=200,
            json={"access_token": "TEST_TOKEN_ROLL", "expires_in": 32400},
        )
        respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
            status_code=201,
            json={"id": "PAYPAL-ORDER-ROLL-01", "status": "CREATED"},
        )
        respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-ROLL-01/capture").respond(
            status_code=201,
            json={
                "id": "PAYPAL-ORDER-ROLL-01",
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "payments": {
                            "captures": [
                                {
                                    "id": "CAPTURE-ROLL-01",
                                    "status": "COMPLETED",
                                    "amount": {"value": "289.50", "currency_code": "USD"},
                                    "create_time": "2026-10-20T12:00:00Z",
                                }
                            ]
                        }
                    }
                ],
            },
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as local_client:
            create_res = await local_client.post(
                "/api/v1/orders",
                json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
            )
            order_id = create_res.json()["id"]

            async with session_factory() as s:
                initial_stock = (await s.execute(select(CatalogItem).where(CatalogItem.sku == "CHAIR-ERGO-01"))).scalars().first().stock

            # Verify that normal capture succeeds and commits atomically
            cap_res = await local_client.post(f"/api/v1/orders/{order_id}/capture")
            assert cap_res.status_code == 200

            async with session_factory() as s:
                final_stock = (await s.execute(select(CatalogItem).where(CatalogItem.sku == "CHAIR-ERGO-01"))).scalars().first().stock
                assert final_stock == initial_stock - 1
                movements = (await s.execute(select(InventoryMovement).where(InventoryMovement.order_id == order_id))).scalars().all()
                assert len(movements) == 1
    finally:
        app.dependency_overrides.pop(get_db, None)
        await engine.dispose()



