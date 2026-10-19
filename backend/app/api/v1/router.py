from fastapi import APIRouter
from app.api.v1.catalog import router as catalog_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(catalog_router)
