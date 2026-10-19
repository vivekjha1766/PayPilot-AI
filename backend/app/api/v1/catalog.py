from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.catalog import CatalogItem
from app.schemas.catalog import CatalogItemResponse

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("", response_model=List[CatalogItemResponse])
async def list_catalog_items(
    db: AsyncSession = Depends(get_db),
) -> List[CatalogItemResponse]:
    """
    Retrieve authoritative catalog items from the database.
    Prices are maintained as Decimal and serialized as decimal strings.
    """
    stmt = select(CatalogItem).order_by(CatalogItem.id.asc())
    result = await db.execute(stmt)
    items = result.scalars().all()
    return list(items)
