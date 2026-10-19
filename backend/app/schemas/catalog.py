from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_serializer


class CatalogItemResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: str
    unit_price: Decimal
    currency: str
    stock: int
    category: str

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("unit_price")
    def serialize_unit_price(self, v: Decimal) -> str:
        return f"{Decimal(str(v)):.2f}"
