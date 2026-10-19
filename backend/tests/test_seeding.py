import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seed import seed_catalog, SEEDED_CATALOG_ITEMS
from app.models.catalog import CatalogItem


@pytest.mark.asyncio
async def test_seeding_is_idempotent(db_session: AsyncSession):
    # db_session fixture already seeds once
    count_stmt = select(func.count()).select_from(CatalogItem)
    result = await db_session.execute(count_stmt)
    initial_count = result.scalar()

    assert initial_count == len(SEEDED_CATALOG_ITEMS)

    # Calling seed_catalog a second time must add 0 items and cause no duplicate SKU errors
    second_run_added = await seed_catalog(db_session)
    assert second_run_added == 0

    result2 = await db_session.execute(count_stmt)
    after_count = result2.scalar()
    assert after_count == initial_count
