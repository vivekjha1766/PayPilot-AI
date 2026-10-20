import asyncio
from decimal import Decimal
import pytest
import respx
from httpx import AsyncClient

from app.core.config import settings
from app.models.order import Order, OrderStatus
from sqlalchemy import select

BASE_URL = settings.paypal_base_url


@pytest.mark.asyncio
async def test_payment_config_endpoint_no_client_secret_leakage(client: AsyncClient):
    response = await client.get("/api/v1/payments/config")
    assert response.status_code == 200
    data = response.json()

    assert "client_id" in data
    assert data["client_id"] == "test_sandbox_client_id_12345"
    assert "currency" in data
    assert "is_configured" in data
    assert "sandbox" in data

    # STRICT SECURITY CHECK: Ensure secret or tokens are NEVER leaked
    assert "client_secret" not in data
    assert "secret" not in data
    assert "access_token" not in data


@pytest.mark.asyncio
@respx.mock
async def test_create_order_success(client: AsyncClient):
    # Mock PayPal OAuth and order creation
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_1", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-123", "status": "CREATED"},
    )

    payload = {
        "items": [
            {"sku": "CHAIR-ERGO-01", "quantity": 2}
        ]
    }
    response = await client.post("/api/v1/orders", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["status"] == "CREATED"
    assert data["paypal_order_id"] == "PAYPAL-ORDER-123"
    # Unit price is 289.50 * 2 = 579.00
    assert data["total_amount"] == "579.00"
    assert data["currency"] == "USD"
    assert len(data["items"]) == 1
    assert data["items"][0]["sku"] == "CHAIR-ERGO-01"
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["unit_price"] == "289.50"
    assert data["items"][0]["total_price"] == "579.00"

    # Audit log entry check
    assert len(data["audit_logs"]) >= 2
    event_types = [log["event_type"] for log in data["audit_logs"]]
    assert "ORDER_CREATED" in event_types
    assert "PAYPAL_ORDER_CREATED" in event_types


@pytest.mark.asyncio
async def test_create_order_invalid_quantity_rejected(client: AsyncClient):
    # Zero quantity
    res_zero = await client.post("/api/v1/orders", json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 0}]})
    assert res_zero.status_code == 422 or res_zero.status_code == 400

    # Negative quantity
    res_neg = await client.post("/api/v1/orders", json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": -3}]})
    assert res_neg.status_code == 422 or res_neg.status_code == 400


@pytest.mark.asyncio
async def test_create_order_exceeds_stock_rejected(client: AsyncClient):
    # SKU CHAIR-ERGO-01 has stock 45
    response = await client.post("/api/v1/orders", json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 9999}]})
    assert response.status_code == 400
    assert "exceeds available stock" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_order_nonexistent_item_rejected(client: AsyncClient):
    response = await client.post("/api/v1/orders", json={"items": [{"sku": "NON-EXISTENT-SKU-999", "quantity": 1}]})
    assert response.status_code == 404
    assert "not found in database" in response.json()["detail"]


@pytest.mark.asyncio
@respx.mock
async def test_create_order_price_tampering_prevented(client: AsyncClient):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_1", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-TAMPER-TEST", "status": "CREATED"},
    )

    # Malicious client tries to inject price: 1.00 instead of authoritative price 289.50
    malicious_payload = {
        "items": [
            {"sku": "CHAIR-ERGO-01", "quantity": 1, "unit_price": "1.00", "price": "1.00"}
        ]
    }
    response = await client.post("/api/v1/orders", json=malicious_payload)
    assert response.status_code == 201
    data = response.json()

    # The backend must strictly ignore client-provided prices and enforce 289.50
    assert data["total_amount"] == "289.50"
    assert data["items"][0]["unit_price"] == "289.50"


@pytest.mark.asyncio
@respx.mock
async def test_capture_order_success_and_stock_deduction(client: AsyncClient, db_session):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_1", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-CAP-1", "status": "CREATED"},
    )

    # 1. Create order for 1 chair
    order_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_data = order_res.json()
    order_id = order_data["id"]

    # 2. Mock PayPal capture
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-CAP-1/capture").respond(
        status_code=201,
        json={
            "id": "PAYPAL-ORDER-CAP-1",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-ABC-123",
                                "status": "COMPLETED",
                                "amount": {"currency_code": "USD", "value": "289.50"},
                                "create_time": "2026-10-20T12:00:00Z",
                            }
                        ]
                    }
                }
            ],
        },
    )

    # 3. Call capture
    cap_res = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap_res.status_code == 200
    cap_data = cap_res.json()

    assert cap_data["status"] == "COMPLETED"
    assert cap_data["paypal_capture_id"] == "CAPTURE-ABC-123"
    assert cap_data["captured_amount"] == "289.50"
    assert cap_data["currency"] == "USD"

    # Verify order state in GET /orders/{order_id}
    get_res = await client.get(f"/api/v1/orders/{order_id}")
    assert get_res.status_code == 200
    final_order = get_res.json()
    assert final_order["status"] == "COMPLETED"
    assert final_order["paypal_capture_id"] == "CAPTURE-ABC-123"


@pytest.mark.asyncio
@respx.mock
async def test_duplicate_capture_requests_idempotent(client: AsyncClient):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_1", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-DUP-1", "status": "CREATED"},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-DUP-1/capture").respond(
        status_code=201,
        json={
            "id": "PAYPAL-ORDER-DUP-1",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-DUP-001",
                                "status": "COMPLETED",
                                "amount": {"currency_code": "USD", "value": "289.50"},
                            }
                        ]
                    }
                }
            ],
        },
    )

    order_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_id = order_res.json()["id"]

    # First capture
    cap1 = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap1.status_code == 200
    assert cap1.json()["status"] == "COMPLETED"

    # Second capture request on already COMPLETED order must return the verified receipt safely
    cap2 = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap2.status_code == 200
    assert cap2.json()["status"] == "COMPLETED"
    assert cap2.json()["paypal_capture_id"] == "CAPTURE-DUP-001"


@pytest.mark.asyncio
@respx.mock
async def test_concurrent_capture_attempt_rejected(client: AsyncClient, db_session):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_1", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-CONC-1", "status": "CREATED"},
    )

    order_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_id = order_res.json()["id"]

    # Manually mark order status as CAPTURING in DB to simulate an active concurrent capture
    stmt = select(Order).where(Order.id == order_id)
    result = await db_session.execute(stmt)
    order = result.scalars().first()
    order.status = "CAPTURING"
    await db_session.commit()

    # Second attempt while in CAPTURING must be rejected with 409 Conflict
    cap_res = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap_res.status_code == 409
    assert "already in progress" in cap_res.json()["detail"]


@pytest.mark.asyncio
@respx.mock
async def test_buyer_cancellation(client: AsyncClient):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_1", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-CANCEL-1", "status": "CREATED"},
    )

    order_res = await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )
    order_id = order_res.json()["id"]

    # Buyer cancels
    cancel_res = await client.post(f"/api/v1/orders/{order_id}/cancel")
    assert cancel_res.status_code == 200
    data = cancel_res.json()
    assert data["status"] == "CANCELLED"

    # Capture on CANCELLED order must fail
    cap_res = await client.post(f"/api/v1/orders/{order_id}/capture")
    assert cap_res.status_code == 400
    assert "not eligible for capture" in cap_res.json()["detail"]


@pytest.mark.asyncio
@respx.mock
async def test_list_orders_persisted_transaction_history(client: AsyncClient):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TEST_TOKEN_1", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-HIST-1", "status": "CREATED"},
    )

    # Create an order
    await client.post(
        "/api/v1/orders",
        json={"items": [{"sku": "CHAIR-ERGO-01", "quantity": 1}]},
    )

    # Fetch transaction list
    history_res = await client.get("/api/v1/orders")
    assert history_res.status_code == 200
    orders = history_res.json()
    assert isinstance(orders, list)
    assert len(orders) >= 1
    assert "total_amount" in orders[0]
    assert "paypal_order_id" in orders[0]
    assert "audit_logs" in orders[0]

