from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.catalog import CatalogItem

SEEDED_CATALOG_ITEMS: List[Dict[str, Any]] = [
    {
        "sku": "CHAIR-ERGO-01",
        "name": "AeroPro Ergonomic Mesh Chair",
        "description": "High-back breathable mesh desk chair with 3D adjustable armrests and dynamic lumbar support.",
        "unit_price": Decimal("289.50"),
        "currency": "USD",
        "stock": 45,
        "category": "Furniture",
    },
    {
        "sku": "DESK-STAND-02",
        "name": "ApexLift Dual-Motor Standing Desk (60x30)",
        "description": "Solid bamboo electric height-adjustable workstation with 4 memory presets and cable management tray.",
        "unit_price": Decimal("499.00"),
        "currency": "USD",
        "stock": 20,
        "category": "Furniture",
    },
    {
        "sku": "MON-CURVE-03",
        "name": "ViewMaster 34-Inch Curved UltraWide Monitor",
        "description": "1440p WQHD IPS display, 100Hz refresh rate, USB-C 90W power delivery, and built-in KVM switch.",
        "unit_price": Decimal("549.99"),
        "currency": "USD",
        "stock": 18,
        "category": "Displays",
    },
    {
        "sku": "KB-SPLIT-04",
        "name": "ErgoType Wireless Split Mechanical Keyboard",
        "description": "Hot-swappable tactile switches, Bluetooth multi-device pairing, and cushioned magnetic palm rests.",
        "unit_price": Decimal("159.00"),
        "currency": "USD",
        "stock": 60,
        "category": "Peripherals",
    },
    {
        "sku": "AUDIO-HEADSET-05",
        "name": "ClearVoice Pro ANC Wireless Headset",
        "description": "Hybrid active noise cancellation, AI beamforming boom microphone, and 35-hour talk time battery.",
        "unit_price": Decimal("199.95"),
        "currency": "USD",
        "stock": 35,
        "category": "Audio",
    },
    {
        "sku": "DOCK-TB4-06",
        "name": "OmniPort Thunderbolt 4 Docking Station",
        "description": "Single-cable 11-in-1 dock with dual 4K display support, 2.5GbE LAN, and 96W laptop charging.",
        "unit_price": Decimal("229.00"),
        "currency": "USD",
        "stock": 25,
        "category": "Accessories",
    },
    {
        "sku": "LAMP-LIGHTBAR-07",
        "name": "LuminaScreen Smart Monitor Light Bar",
        "description": "Asymmetric optical design prevents screen glare, with wireless rotary control dial and auto-dimming.",
        "unit_price": Decimal("69.99"),
        "currency": "USD",
        "stock": 50,
        "category": "Lighting",
    },
    {
        "sku": "MAT-FLOOR-08",
        "name": "StrideRelief Ergonomic Anti-Fatigue Mat",
        "description": "Multi-terrain contoured standing mat engineered with high-density foam to reduce leg and back strain.",
        "unit_price": Decimal("49.50"),
        "currency": "USD",
        "stock": 40,
        "category": "Accessories",
    },
]


async def seed_catalog(session: AsyncSession) -> int:
    """
    Seeds catalog items deterministically if they do not already exist.
    Returns the count of newly inserted items.
    """
    added_count = 0
    for item_data in SEEDED_CATALOG_ITEMS:
        stmt = select(CatalogItem).where(CatalogItem.sku == item_data["sku"])
        result = await session.execute(stmt)
        existing = result.scalars().first()
        if not existing:
            item = CatalogItem(**item_data)
            session.add(item)
            added_count += 1

    if added_count > 0:
        await session.commit()

    return added_count
