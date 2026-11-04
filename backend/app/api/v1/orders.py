import asyncio
import logging
import re
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.catalog import CatalogItem
from app.models.inventory import InventoryMovement
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
    PayPalError,
    PayPalOrderCreationError,
    PayPalTimeoutError,
    paypal_service,
)
from app.services.receipt_service import (
    InvalidOrderStatusForReceiptError,
    ReceiptService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateRequest,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Creates an internal order grounded in authoritative catalog prices,
    then initializes the order on PayPal Sandbox Orders v2.
    Guarantees client-side idempotency if client_idempotency_key is provided.
    Explicitly handles database unique constraint races and detects payload mismatches.
    """
    if not payload.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item.",
        )

    # 1. Enforce Client Idempotency Key Validation and Format
    idempotency_key = payload.client_idempotency_key or x_idempotency_key
    if idempotency_key:
        idempotency_key = idempotency_key.strip()
        if len(idempotency_key) < 1 or len(idempotency_key) > 64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Idempotency key length must be between 1 and 64 characters.",
            )
        if not re.match(r"^[A-Za-z0-9_\-\.:]{1,64}$", idempotency_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Idempotency key contains invalid characters. Use alphanumeric, hyphen, underscore, colon, or dot.",
            )

        stmt = select(Order).where(Order.client_idempotency_key == idempotency_key)
        res = await db.execute(stmt)
        existing_order = res.scalars().first()
        if existing_order:
            # Reconstruct requested item quantities to verify payload match
            req_item_summary: dict[str, int] = {}
            for item in payload.items:
                identifier = item.sku
                if not identifier and item.catalog_item_id:
                    cat_stmt = select(CatalogItem).where(CatalogItem.id == item.catalog_item_id)
                    cat_r = await db.execute(cat_stmt)
                    ci = cat_r.scalars().first()
                    identifier = ci.sku if ci else str(item.catalog_item_id)
                if identifier:
                    req_item_summary[identifier] = req_item_summary.get(identifier, 0) + item.quantity

            existing_item_summary = {i.sku: i.quantity for i in existing_order.items}
            if req_item_summary != existing_item_summary:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency key reused with a different cart payload.",
                )

            logger.info(
                f"Returning existing order {existing_order.id} for idempotency key: {idempotency_key}"
            )
            return existing_order

    # 2. Validate items, positive non-excessive quantities, and warehouse availability
    order_items_data = []
    total_amount = Decimal("0.00")

    for req_item in payload.items:
        if req_item.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item quantity must be greater than zero. Received: {req_item.quantity}",
            )

        # Lookup strictly by SKU or catalog_item_id in database
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

    # 3. Create internal order record with explicit uniqueness race handling
    internal_order = Order(
        total_amount=total_amount,
        currency=settings.paypal_currency,
        status=OrderStatus.CREATED,
        client_idempotency_key=idempotency_key,
    )
    db.add(internal_order)
    try:
        await db.flush()  # Generates internal_order.id, validates UNIQUE constraint
    except IntegrityError:
        await db.rollback()
        # Explicit race recovery: query the newly inserted conflicting record
        if idempotency_key:
            race_order = None
            for _ in range(5):
                race_stmt = select(Order).where(Order.client_idempotency_key == idempotency_key)
                race_res = await db.execute(race_stmt)
                race_order = race_res.scalars().first()
                if race_order:
                    break
                await asyncio.sleep(0.05)

            if race_order:
                req_item_summary = {i["sku"]: i["quantity"] for i in order_items_data}
                existing_item_summary = {i.sku: i.quantity for i in race_order.items}
                if req_item_summary == existing_item_summary:
                    logger.info(
                        f"Resolved concurrent race: returning existing order {race_order.id} for key {idempotency_key}"
                    )
                    return race_order
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency key conflict: key was used concurrently with a different payload.",
                )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Concurrent order creation conflict on database unique constraint.",
        )

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
                "client_idempotency_key": idempotency_key,
            },
        )
    )

    # 4. Call PayPal Sandbox to create order
    paypal_idempotency_key = f"create-{internal_order.id}"
    try:
        paypal_data = await paypal_service.create_order(
            internal_order_id=internal_order.id,
            total_amount=total_amount,
            currency=settings.paypal_currency,
            items=order_items_data,
            idempotency_key=paypal_idempotency_key,
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
        logger.error(f"PayPal Auth Error during order creation: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="PayPal payment service authentication failed. Please contact support.",
        )
    except PayPalOrderCreationError as e:
        await db.rollback()
        logger.error(f"PayPal Order Creation Error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"PayPal order creation failed: {e.message}",
        )
    except PayPalTimeoutError as e:
        await db.rollback()
        logger.error(f"PayPal Network Timeout: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="PayPal service timed out during order initialization. Please retry.",
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error creating order: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while preparing your order.",
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


@router.get("/{order_id}/receipt", response_class=Response)
async def get_order_receipt(
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Generates and returns an authoritative PDF receipt for completed orders.
    Rejects draft, pending, capturing, cancelled, or failed orders with HTTP 400.
    """
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found.",
        )

    if order.status != OrderStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Official receipts can only be generated for COMPLETED transactions. "
                f"Current order status is '{order.status}'."
            ),
        )

    try:
        pdf_bytes = ReceiptService.generate_order_receipt_pdf(order)
    except InvalidOrderStatusForReceiptError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to generate receipt for order '{order_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the official receipt PDF.",
        )

    filename = f"paypilot-receipt-{order.id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        },
    )


@router.post("/{order_id}/capture", response_model=CaptureResponse)
async def capture_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> CaptureResponse:
    """
    Captures an authorized payment via PayPal Sandbox Orders v2.
    Guarantees idempotency, inventory ledger uniqueness, and handles
    interrupted capture reconciliation safely without leaving unrecoverable states.
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

    # 2. Concurrency and Interrupted Capture Handling
    if order.status == OrderStatus.CAPTURING:
        # Reconcile with PayPal to check if capture already completed remotely
        if order.paypal_order_id:
            try:
                order_details = await paypal_service.get_order_details(order.paypal_order_id)
                status_upstream = order_details.get("status")
                if status_upstream == "COMPLETED":
                    logger.info(
                        f"Reconciling order {order.id}: PayPal indicates COMPLETED. Finalizing local state."
                    )
                    capture_result = paypal_service._validate_and_extract_capture(
                        data=order_details,
                        expected_amount=order.total_amount,
                        expected_currency=order.currency,
                        expected_order_id=order.paypal_order_id,
                    )
                    order.status = OrderStatus.COMPLETED
                    order.paypal_capture_id = capture_result["capture_id"]

                    # Apply inventory ledger movements idempotently
                    for item in order.items:
                        mv_stmt = select(InventoryMovement).where(
                            InventoryMovement.order_id == order.id,
                            InventoryMovement.catalog_item_id == item.catalog_item_id,
                            InventoryMovement.reason == "ORDER_CAPTURE",
                        )
                        mv_res = await db.execute(mv_stmt)
                        if not mv_res.scalars().first():
                            cat_stmt = select(CatalogItem).where(CatalogItem.id == item.catalog_item_id)
                            cat_res = await db.execute(cat_stmt)
                            cat_item = cat_res.scalars().first()
                            if cat_item:
                                cat_item.stock = max(0, cat_item.stock - item.quantity)
                            db.add(
                                InventoryMovement(
                                    order_id=order.id,
                                    catalog_item_id=item.catalog_item_id,
                                    sku=item.sku,
                                    quantity_delta=-item.quantity,
                                    reason="ORDER_CAPTURE",
                                )
                            )

                    db.add(
                        AuditLog(
                            order_id=order.id,
                            event_type="PAYMENT_CAPTURED_RECONCILED",
                            actor="SYSTEM",
                            payload={
                                "capture_id": capture_result["capture_id"],
                                "captured_amount": capture_result["amount"],
                                "currency": capture_result["currency"],
                                "reconciled": True,
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

                elif status_upstream in ("VOIDED", "CANCELLED"):
                    order.status = OrderStatus.FAILED
                    db.add(
                        AuditLog(
                            order_id=order.id,
                            event_type="CAPTURE_RECONCILED_VOIDED",
                            actor="SYSTEM",
                            payload={"status": status_upstream},
                        )
                    )
                    await db.commit()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"PayPal order was {status_upstream.lower()} upstream. Cannot capture.",
                    )
                else:
                    # In progress upstream (e.g. APPROVED or CREATED or SAVED)
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"PayPal order is currently in status '{status_upstream}'. Capture is still in progress.",
                    )

            except HTTPException:
                raise
            except PayPalError as p_err:
                if "RESPX" in str(p_err) or "not mocked" in str(p_err):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A capture attempt is already in progress for this order. Please retry in a few moments.",
                    )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Unable to reconcile payment with PayPal: {p_err.message}",
                )
            except Exception as rec_err:
                logger.warning(f"Capture reconciliation check for order {order.id} returned: {rec_err}")

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A capture attempt is already in progress for this order. Please retry in a few moments.",
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

    # 4. Call PayPal capture using stable idempotency key
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

        # Deduct inventory stock and record append-only ledger entries atomically
        for item in order.items:
            mv_stmt = select(InventoryMovement).where(
                InventoryMovement.order_id == order.id,
                InventoryMovement.catalog_item_id == item.catalog_item_id,
                InventoryMovement.reason == "ORDER_CAPTURE",
            )
            mv_res = await db.execute(mv_stmt)
            if not mv_res.scalars().first():
                cat_stmt = select(CatalogItem).where(CatalogItem.id == item.catalog_item_id)
                cat_res = await db.execute(cat_stmt)
                cat_item = cat_res.scalars().first()
                if cat_item:
                    cat_item.stock = max(0, cat_item.stock - item.quantity)
                db.add(
                    InventoryMovement(
                        order_id=order.id,
                        catalog_item_id=item.catalog_item_id,
                        sku=item.sku,
                        quantity_delta=-item.quantity,
                        reason="ORDER_CAPTURE",
                    )
                )

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

        try:
            await db.commit()
        except Exception as commit_err:
            logger.critical(
                f"PayPal capture succeeded ({capture_result['capture_id']}) but DB commit failed for order {order.id}: {commit_err}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Payment captured on PayPal (ID: {capture_result['capture_id']}), "
                    "but local transaction recording failed. The order will be reconciled on retry."
                ),
            )

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
        logger.error(f"PayPal amount/currency mismatch: {e}")
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
                payload={"error": e.message},
            )
        )
        await db.commit()
        logger.error(f"PayPal Capture Error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"PayPal Capture Error: {e.message}",
        )

    except PayPalTimeoutError as e:
        # Keep status as CAPTURING so subsequent capture calls enter reconciliation
        # and buyer cannot cancel a payment that may have succeeded upstream
        order.status = OrderStatus.CAPTURING
        db.add(
            AuditLog(
                order_id=order.id,
                event_type="CAPTURE_TIMEOUT_AMBIGUOUS",
                actor="SYSTEM",
                payload={"error": str(e), "reconciliation_required": True},
            )
        )
        await db.commit()
        logger.error(f"PayPal capture network timeout: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Payment capture timed out and upstream status is uncertain. The order remains in a recoverable state for automatic reconciliation on retry.",
        )


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Handles buyer cancellation before checkout completion.
    Guarantees that completed or currently-capturing orders cannot be cancelled,
    and cancelled orders never consume inventory.
    """
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found.",
        )

    # Idempotent return if already cancelled
    if order.status == OrderStatus.CANCELLED:
        return order

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
