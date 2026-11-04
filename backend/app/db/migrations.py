import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

logger = logging.getLogger(__name__)


async def run_migrations(conn: AsyncConnection) -> None:
    """
    Applies idempotent, safe schema migrations for SQLite.
    Guarantees that existing tables and records (including completed orders)
    remain completely intact.
    """
    # 1. Check if client_idempotency_key exists on orders
    result = await conn.execute(text("PRAGMA table_info(orders);"))
    columns = [row[1] for row in result.fetchall()]

    if "client_idempotency_key" not in columns:
        logger.info("Migrating: Adding client_idempotency_key column to orders table")
        await conn.execute(
            text("ALTER TABLE orders ADD COLUMN client_idempotency_key VARCHAR(64);")
        )
        await conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_orders_client_idempotency_key "
                "ON orders (client_idempotency_key);"
            )
        )

    # 2. Ensure inventory_movements ledger table exists
    logger.info("Migrating: Ensuring inventory_movements table exists")
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS inventory_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id VARCHAR(36) NOT NULL,
                catalog_item_id INTEGER NOT NULL,
                sku VARCHAR(64) NOT NULL,
                quantity_delta INTEGER NOT NULL,
                reason VARCHAR(64) NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (catalog_item_id) REFERENCES catalog_items(id),
                CONSTRAINT uq_inventory_movement_order_item_reason UNIQUE (order_id, catalog_item_id, reason)
            );
            """
        )
    )
    await conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_inventory_movements_order_id ON inventory_movements (order_id);"
        )
    )
    await conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_inventory_movements_catalog_item_id ON inventory_movements (catalog_item_id);"
        )
    )
    await conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_inventory_movements_sku ON inventory_movements (sku);"
        )
    )
    await conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_inventory_movements_reason ON inventory_movements (reason);"
        )
    )
