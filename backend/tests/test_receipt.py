import uuid
from decimal import Decimal
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem, OrderStatus
from app.services.receipt_service import InvalidOrderStatusForReceiptError, ReceiptService


@pytest.mark.asyncio
async def test_generate_pdf_receipt_for_completed_order(client: AsyncClient, db_session: AsyncSession):
    """Verify that a completed order returns an authoritative PDF receipt starting with %PDF-."""
    order_id = str(uuid.uuid4())
    completed_order = Order(
        id=order_id,
        status=OrderStatus.COMPLETED,
        total_amount=Decimal("289.50"),
        currency="USD",
        paypal_order_id="TEST-PAYPAL-ORDER-001",
        paypal_capture_id="TEST-PAYPAL-CAPTURE-001",
    )
    db_session.add(completed_order)
    await db_session.flush()

    item = OrderItem(
        order_id=order_id,
        catalog_item_id=1,
        sku="CHAIR-ERGO-01",
        name="Ergonomic Executive Chair",
        quantity=1,
        unit_price=Decimal("289.50"),
        total_price=Decimal("289.50"),
    )
    db_session.add(item)
    await db_session.commit()

    response = await client.get(f"/api/v1/orders/{order_id}/receipt")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert f'filename="paypilot-receipt-{order_id[:8]}.pdf"' in response.headers.get("content-disposition", "")
    assert response.content.startswith(b"%PDF-")
    assert len(response.content) > 500


@pytest.mark.asyncio
async def test_receipt_forbidden_for_cancelled_order(client: AsyncClient, db_session: AsyncSession):
    """Verify that cancelled orders return HTTP 400 Bad Request."""
    order_id = str(uuid.uuid4())
    cancelled_order = Order(
        id=order_id,
        status=OrderStatus.CANCELLED,
        total_amount=Decimal("150.00"),
        currency="USD",
    )
    db_session.add(cancelled_order)
    await db_session.commit()

    response = await client.get(f"/api/v1/orders/{order_id}/receipt")
    assert response.status_code == 400
    data = response.json()
    assert "only be generated for completed" in data["detail"].lower()


@pytest.mark.asyncio
async def test_receipt_forbidden_for_created_order(client: AsyncClient, db_session: AsyncSession):
    """Verify that pending/created orders cannot receive a paid receipt."""
    order_id = str(uuid.uuid4())
    created_order = Order(
        id=order_id,
        status=OrderStatus.CREATED,
        total_amount=Decimal("99.00"),
        currency="USD",
    )
    db_session.add(created_order)
    await db_session.commit()

    response = await client.get(f"/api/v1/orders/{order_id}/receipt")
    assert response.status_code == 400
    data = response.json()
    assert "only be generated for completed" in data["detail"].lower()


@pytest.mark.asyncio
async def test_receipt_for_nonexistent_order_returns_404(client: AsyncClient):
    """Verify that querying a receipt for an unknown order returns HTTP 404."""
    response = await client.get("/api/v1/orders/non-existent-order-uuid-9999/receipt")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_receipt_service_direct_unit_test():
    """Verify ReceiptService raises InvalidOrderStatusForReceiptError directly on invalid status."""
    dummy_order = Order(
        id=str(uuid.uuid4()),
        status=OrderStatus.FAILED,
        total_amount=Decimal("50.00"),
        currency="USD",
    )
    with pytest.raises(InvalidOrderStatusForReceiptError) as exc_info:
        ReceiptService.generate_order_receipt_pdf(dummy_order)
    assert "only be generated for completed" in str(exc_info.value).lower()

