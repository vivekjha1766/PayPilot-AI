from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator


class PaymentConfigResponse(BaseModel):
    client_id: str
    currency: str
    is_configured: bool
    sandbox: bool = True


class OrderItemCreate(BaseModel):
    sku: Optional[str] = None
    catalog_item_id: Optional[int] = None
    quantity: int = Field(gt=0, description="Quantity must be a positive integer")

    @model_validator(mode="after")
    def check_identifier(self) -> "OrderItemCreate":
        if not self.sku and not self.catalog_item_id:
            raise ValueError("Either 'sku' or 'catalog_item_id' must be provided.")
        return self


class OrderCreateRequest(BaseModel):
    items: List[OrderItemCreate] = Field(min_length=1, description="At least one item required")
    client_idempotency_key: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Optional unique client idempotency key to prevent duplicate orders",
    )


class OrderItemResponse(BaseModel):
    id: int
    catalog_item_id: int
    sku: str
    name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("unit_price")
    def serialize_unit_price(self, v: Decimal) -> str:
        return f"{Decimal(str(v)):.2f}"

    @field_serializer("total_price")
    def serialize_total_price(self, v: Decimal) -> str:
        return f"{Decimal(str(v)):.2f}"


class AuditLogResponse(BaseModel):
    id: int
    event_type: str
    actor: str
    payload: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: str
    status: str
    total_amount: Decimal
    currency: str
    paypal_order_id: Optional[str] = None
    paypal_capture_id: Optional[str] = None
    client_idempotency_key: Optional[str] = None
    items: List[OrderItemResponse] = []
    audit_logs: List[AuditLogResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("total_amount")
    def serialize_total_amount(self, v: Decimal) -> str:
        return f"{Decimal(str(v)):.2f}"


class CaptureResponse(BaseModel):
    order_id: str
    status: str
    paypal_order_id: str
    paypal_capture_id: str
    captured_amount: str
    currency: str
    captured_at: Optional[str] = None
