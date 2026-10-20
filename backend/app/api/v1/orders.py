from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.catalog import CatalogItem
from app.models.order import AuditLog, Order, OrderItem, OrderStatus
from app.schemas.order import (
    CaptureResponse,
    OrderCreateRequest,
    OrderResponse,
)
from app.services.paypal_service import (
    PayPalAmountMismatchError,
    PayPalAuthError,
    PayPalCaptureError,
    PayPalOrderCreationError,
    PayPalTimeoutError,
    paypal_service,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Creates an internal order grounded in authoritative catalog prices,
    then initializes the order on PayPal Sandbox Orders v2.
    """
    if not payload.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item.",
        )

    # Validate items and quantities against database catalog
    order_items_data = []
    total_amount = Decimal("0.00")

    for req_item in payload.items:
        if req_item.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item quantity must be greater than zero. Received: {req_item.quantity}",
            )

        # Lookup by SKU or catalog_item_id
        if req_item.sku:
            stmt = select(CatalogItem).where(CatalogItem.sku == req_item.sku)
        else:
            stmt = select(CatalogItem).where(CatalogItem.id == req_item.catalog_item_id)

        result = await db.execute(stmt)
        catalog_item = result.scalars().first()

        if not catalog_item:
            identifier = req_item.sku or req_item.catalog_item_id
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Catalog item '{identifier}' not found in database.",
            )

        if req_item.quantity > catalog_item.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Requested quantity {req_item.quantity} for '{catalog_item.name}' "
                    f"exceeds available stock ({catalog_item.stock})."
                ),
            )

        # Calculate authoritative prices strictly from database
        unit_price = Decimal(str(catalog_item.unit_price))
        item_total = unit_price * Decimal(req_item.quantity)
        total_amount += item_total

        order_items_data.append({
            "catalog_item_id": catalog_item.id,
            "sku": catalog_item.sku,
            "name": catalog_item.name,
            "quantity": req_item.quantity,
            "unit_price": unit_price,
            "total_price": item_total,
        })

    # Create internal order record
    internal_order = Order(
        total_amount=total_amount,
        currency=settings.paypal_currency,
        status=OrderStatus.CREATED,
    )
    db.add(internal_order)
    await db.flush()  # Generates internal_order.id

    for item_data in order_items_data:
        db_item = OrderItem(
            order_id=internal_order.id,
            catalog_item_id=item_data["catalog_item_id"],
            sku=item_data["sku"],
            name=item_data["name"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            total_price=item_data["total_price"],
        )
        db.add(db_item)

    # Record audit log
    db.add(
        AuditLog(
            order_id=internal_order.id,
            event_type="ORDER_CREATED",
            actor="SYSTEM",
            payload={
                "order_id": internal_order.id,
                "total_amount": str(total_amount),
                "currency": settings.paypal_currency,
                "item_count": len(order_items_data),
            },
        )
    )

    # Call PayPal Sandbox to create order
    idempotency_key = f"create-{internal_order.id}"
    try:
        paypal_data = await paypal_service.create_order(
            internal_order_id=internal_order.id,
            total_amount=total_amount,
            currency=settings.paypal_currency,
            items=order_items_data,
            idempotency_key=idempotency_key,
        )
        internal_order.paypal_order_id = paypal_data["id"]

        db.add(
            AuditLog(
                order_id=internal_order.id,
                event_type="PAYPAL_ORDER_CREATED",
                actor="PAYPAL_SANDBOX",
                payload={"paypal_order_id": paypal_data["id"]},
            )
        )
        await db.commit()
        await db.refresh(internal_order)

    except PayPalAuthError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"PayPal Authentication Error: {e.message}",
        )
    except PayPalOrderCreationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"PayPal Order Creation Error: {e.message}",
        )
    except PayPalTimeoutError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"PayPal Network Timeout: {e.message}",
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error creating order: {str(e)}",
        )

    return internal_order


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> List[OrderResponse]:
    """
    Retrieves persisted transaction history ordered by creation date descending.
    """
    stmt = select(Order).order_by(Order.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    orders = result.scalars().all()
    return list(orders)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Retrieves internal order details and its complete audit history.
    """
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found.",
        )
    return order


@router.post("/{order_id}/capture", response_model=CaptureResponse)
async def capture_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> CaptureResponse:
    """
    Captures an authorized payment via PayPal Sandbox Orders v2.
    Guarantees idempotency and prevents concurrent or duplicate captures.
    """
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found.",
        )

    # 1. Idempotent return if already completed
    if order.status == OrderStatus.COMPLETED:
        return CaptureResponse(
            order_id=order.id,
            status=order.status,
            paypal_order_id=order.paypal_order_id or "",
            paypal_capture_id=order.paypal_capture_id or "",
            captured_amount=f"{Decimal(str(order.total_amount)):.2f}",
            currency=order.currency,
        )

    # 2. Concurrency protection
    if order.status == OrderStatus.CAPTURING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A capture attempt is already in progress for this order.",
        )

    # 3. State eligibility check
    if order.status not in (OrderStatus.CREATED, OrderStatus.APPROVED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order status '{order.status}' is not eligible for capture.",
        )

    if not order.paypal_order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order has no associated PayPal order ID.",
        )

    # Transition state to CAPTURING to guard against concurrent requests
    order.status = OrderStatus.CAPTURING
    db.add(
        AuditLog(
            order_id=order.id,
            event_type="CAPTURE_INITIATED",
            actor="SYSTEM",
            payload={"paypal_order_id": order.paypal_order_id},
        )
    )
    await db.commit()

    # Call PayPal capture using stable idempotency key
    try:
        capture_result = await paypal_service.capture_order(
            paypal_order_id=order.paypal_order_id,
            expected_amount=order.total_amount,
            expected_currency=order.currency,
            idempotency_key=order.capture_idempotency_key,
        )

        # Mark order COMPLETED and record capture ID
        order.status = OrderStatus.COMPLETED
        order.paypal_capture_id = capture_result["capture_id"]

        # Deduct inventory stock
        for item in order.items:
            cat_stmt = select(CatalogItem).where(CatalogItem.id == item.catalog_item_id)
            cat_res = await db.execute(cat_stmt)
            cat_item = cat_res.scalars().first()
            if cat_item:
                cat_item.stock = max(0, cat_item.stock - item.quantity)

        db.add(
            AuditLog(
                order_id=order.id,
                event_type="PAYMENT_CAPTURED",
                actor="PAYPAL_SANDBOX",
                payload={
                    "capture_id": capture_result["capture_id"],
                    "captured_amount": capture_result["amount"],
                    "currency": capture_result["currency"],
                    "captured_at": capture_result.get("captured_at"),
                },
            )
        )
        await db.commit()

        return CaptureResponse(
            order_id=order.id,
            status=order.status,
            paypal_order_id=order.paypal_order_id,
            paypal_capture_id=order.paypal_capture_id,
            captured_amount=capture_result["amount"],
            currency=capture_result["currency"],
            captured_at=capture_result.get("captured_at"),
        )

    except PayPalAmountMismatchError as e:
        order.status = OrderStatus.FAILED
        db.add(
            AuditLog(
                order_id=order.id,
                event_type="CAPTURE_REJECTED_AMOUNT_MISMATCH",
                actor="SYSTEM",
                payload={"error": str(e)},
            )
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security verification error: {str(e)}",
        )

    except PayPalCaptureError as e:
        order.status = OrderStatus.FAILED
        db.add(
            AuditLog(
                order_id=order.id,
                event_type="CAPTURE_FAILED",
                actor="PAYPAL_SANDBOX",
                payload={"error": e.message, "details": e.details},
            )
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"PayPal Capture Error: {e.message}",
        )

    except PayPalTimeoutError as e:
        # Revert status from CAPTURING to CREATED for retry
        order.status = OrderStatus.CREATED
        db.add(
            AuditLog(
                order_id=order.id,
                event_type="CAPTURE_TIMEOUT_AMBIGUOUS",
                actor="SYSTEM",
                payload={"error": str(e)},
            )
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Ambiguous network timeout during capture: {e.message}",
        )


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Handles buyer cancellation before checkout approval.
    """
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found.",
        )

    if order.status in (OrderStatus.COMPLETED, OrderStatus.CAPTURING):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order in status '{order.status}' cannot be cancelled.",
        )

    order.status = OrderStatus.CANCELLED
    db.add(
        AuditLog(
            order_id=order.id,
            event_type="BUYER_CANCELLED",
            actor="BUYER",
            payload={"order_id": order.id, "paypal_order_id": order.paypal_order_id},
        )
    )
    await db.commit()
    await db.refresh(order)
    return order
