from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.order import Order


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

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
        index=True,
    )
    sku: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    quantity_delta: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    order: Mapped["Order"] = relationship("Order", back_populates="inventory_movements")

    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "catalog_item_id",
            "reason",
            name="uq_inventory_movement_order_item_reason",
        ),
    )
