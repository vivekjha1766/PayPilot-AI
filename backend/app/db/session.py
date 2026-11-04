from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings
from app.db.base import Base

connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_async_engine(
    settings.database_url,
    echo=False,
    connect_args=connect_args,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    from app.models.catalog import CatalogItem  # noqa: F401
    from app.models.order import Order, OrderItem, AuditLog  # noqa: F401
    from app.models.inventory import InventoryMovement  # noqa: F401
    from app.db.migrations import run_migrations
    from app.db.seed import seed_catalog

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await run_migrations(conn)

    async with async_session_factory() as session:
        await seed_catalog(session)
