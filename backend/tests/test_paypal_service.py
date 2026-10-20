from decimal import Decimal
import pytest
import respx
import httpx

from app.services.paypal_service import (
    PayPalService,
    PayPalAuthError,
    PayPalOrderCreationError,
    PayPalCaptureError,
    PayPalAmountMismatchError,
    PayPalTimeoutError,
)

BASE_URL = "https://api-m.sandbox.paypal.com"


@pytest.fixture
def service():
    return PayPalService(
        base_url=BASE_URL,
        client_id="test_client_id",
        client_secret="test_client_secret",
        timeout=5.0,
    )


@pytest.mark.asyncio
@respx.mock
async def test_successful_oauth_token_acquisition_and_caching(service):
    # Mock token route
    token_route = respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "ACCESS_TOKEN_XYZ", "expires_in": 32400, "token_type": "Bearer"},
    )

    token1 = await service.get_access_token()
    assert token1 == "ACCESS_TOKEN_XYZ"
    assert token_route.call_count == 1

    # Second call should use cached token without hitting network
    token2 = await service.get_access_token()
    assert token2 == "ACCESS_TOKEN_XYZ"
    assert token_route.call_count == 1


@pytest.mark.asyncio
@respx.mock
async def test_paypal_auth_failure_401(service):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=401,
        json={"error": "invalid_client", "error_description": "Client Authentication failed"},
    )

    with pytest.raises(PayPalAuthError) as exc_info:
        await service.get_access_token()
    assert "Invalid Client ID or Secret" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_successful_order_creation(service):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TOKEN_123", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=201,
        json={"id": "PAYPAL-ORDER-001", "status": "CREATED"},
    )

    items = [{
        "catalog_item_id": 1,
        "sku": "CHAIR-ERGO-01",
        "name": "AeroPro Ergonomic Mesh Chair",
        "quantity": 1,
        "unit_price": Decimal("289.50"),
    }]

    order = await service.create_order(
        internal_order_id="internal-123",
        total_amount=Decimal("289.50"),
        currency="USD",
        items=items,
        idempotency_key="idemp-key-1",
    )
    assert order["id"] == "PAYPAL-ORDER-001"
    assert order["status"] == "CREATED"


@pytest.mark.asyncio
@respx.mock
async def test_order_creation_failure_500(service):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TOKEN_123", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders").respond(
        status_code=500,
        text="Internal Server Error",
    )

    with pytest.raises(PayPalOrderCreationError):
        await service.create_order(
            internal_order_id="internal-123",
            total_amount=Decimal("289.50"),
            currency="USD",
            items=[],
            idempotency_key="idemp-key-1",
        )


@pytest.mark.asyncio
@respx.mock
async def test_capture_success_with_matching_amount_and_currency(service):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TOKEN_123", "expires_in": 32400},
    )
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-001/capture").respond(
        status_code=201,
        json={
            "id": "PAYPAL-ORDER-001",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-999",
                                "status": "COMPLETED",
                                "amount": {"currency_code": "USD", "value": "289.50"},
                                "create_time": "2026-10-20T10:00:00Z",
                            }
                        ]
                    }
                }
            ],
        },
    )

    res = await service.capture_order(
        paypal_order_id="PAYPAL-ORDER-001",
        expected_amount=Decimal("289.50"),
        expected_currency="USD",
        idempotency_key="capture-idemp-1",
    )
    assert res["capture_id"] == "CAPTURE-999"
    assert res["status"] == "COMPLETED"
    assert res["amount"] == "289.50"
    assert res["currency"] == "USD"


@pytest.mark.asyncio
@respx.mock
async def test_capture_amount_mismatch_raises_error(service):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TOKEN_123", "expires_in": 32400},
    )
    # PayPal returned 100.00 instead of 289.50
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-001/capture").respond(
        status_code=201,
        json={
            "id": "PAYPAL-ORDER-001",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-999",
                                "status": "COMPLETED",
                                "amount": {"currency_code": "USD", "value": "100.00"},
                            }
                        ]
                    }
                }
            ],
        },
    )

    with pytest.raises(PayPalAmountMismatchError) as exc_info:
        await service.capture_order(
            paypal_order_id="PAYPAL-ORDER-001",
            expected_amount=Decimal("289.50"),
            expected_currency="USD",
            idempotency_key="capture-idemp-1",
        )
    assert "Amount mismatch" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_capture_missing_capture_id_raises_error(service):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TOKEN_123", "expires_in": 32400},
    )
    # Capture without id
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-001/capture").respond(
        status_code=201,
        json={
            "id": "PAYPAL-ORDER-001",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "status": "COMPLETED",
                                "amount": {"currency_code": "USD", "value": "289.50"},
                            }
                        ]
                    }
                }
            ],
        },
    )

    with pytest.raises(PayPalCaptureError) as exc_info:
        await service.capture_order(
            paypal_order_id="PAYPAL-ORDER-001",
            expected_amount=Decimal("289.50"),
            expected_currency="USD",
            idempotency_key="capture-idemp-1",
        )
    assert "missing capture 'id'" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_capture_timeout_reconciliation_success(service):
    respx.post(f"{BASE_URL}/v1/oauth2/token").respond(
        status_code=200,
        json={"access_token": "TOKEN_123", "expires_in": 32400},
    )
    # Simulate network timeout on capture POST
    respx.post(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-001/capture").mock(
        side_effect=httpx.TimeoutException("Read timed out")
    )
    # Reconciliation call to GET order succeeds and shows COMPLETED
    respx.get(f"{BASE_URL}/v2/checkout/orders/PAYPAL-ORDER-001").respond(
        status_code=200,
        json={
            "id": "PAYPAL-ORDER-001",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "CAPTURE-RECONCILED-888",
                                "status": "COMPLETED",
                                "amount": {"currency_code": "USD", "value": "289.50"},
                                "create_time": "2026-10-20T10:05:00Z",
                            }
                        ]
                    }
                }
            ],
        },
    )

    res = await service.capture_order(
        paypal_order_id="PAYPAL-ORDER-001",
        expected_amount=Decimal("289.50"),
        expected_currency="USD",
        idempotency_key="capture-idemp-1",
    )
    assert res["capture_id"] == "CAPTURE-RECONCILED-888"
    assert res["status"] == "COMPLETED"
