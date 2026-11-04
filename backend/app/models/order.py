import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.inventory import InventoryMovement


class OrderStatus:
    DRAFT = "DRAFT"
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    CAPTURING = "CAPTURING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=OrderStatus.CREATED,
        index=True,
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )
    paypal_order_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=True,
    )
    paypal_capture_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=True,
    )
    capture_idempotency_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    client_idempotency_key: Mapped[Optional[str]] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="AuditLog.created_at.asc()",
        lazy="selectin",
    )
    inventory_movements: Mapped[List["InventoryMovement"]] = relationship(
        "InventoryMovement",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )
    catalog_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("catalog_items.id"),
        nullable=False,
    )
    sku: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    order: Mapped["Order"] = relationship("Order", back_populates="items")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    order_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("orders.id"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    actor: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="audit_logs")
