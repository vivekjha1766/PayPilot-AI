import re
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_catalog_returns_items(client: AsyncClient):
    response = await client.get("/api/v1/catalog")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 8

    # Verify first item structure
    first = items[0]
    assert "id" in first
    assert "sku" in first
    assert "name" in first
    assert "description" in first
    assert "unit_price" in first
    assert "currency" in first
    assert "stock" in first
    assert "category" in first


@pytest.mark.asyncio
async def test_price_representation_is_decimal_string(client: AsyncClient):
    response = await client.get("/api/v1/catalog")
    assert response.status_code == 200
    items = response.json()

    # Regex for standard 2-decimal money format (e.g., "289.50")
    decimal_price_pattern = re.compile(r"^\d+\.\d{2}$")

    for item in items:
        price = item["unit_price"]
        # Must be a string representation of decimal, not a float or integer
        assert isinstance(price, str), f"Expected string price, got {type(price)} for SKU {item['sku']}"
        assert decimal_price_pattern.match(price), f"Price '{price}' does not match decimal pattern ^\\d+\\.\\d{{2}}$"
