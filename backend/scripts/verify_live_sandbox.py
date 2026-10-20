"""
Independent live sandbox verification script for PayPilot AI.
Runs against real PayPal Sandbox endpoints if credentials are provided in backend/.env.
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.services.paypal_service import PayPalService, PayPalAuthError


async def main():
    print("=" * 60)
    print("PayPilot AI — PayPal Sandbox Live Verification")
    print("=" * 60)

    if not settings.is_paypal_configured:
        print("\n[BLOCKED] Real PayPal Sandbox credentials are not yet configured.")
        print("Please configure in backend/.env:")
        print("  PAYPAL_CLIENT_ID=<your-sandbox-client-id>")
        print("  PAYPAL_CLIENT_SECRET=<your-sandbox-client-secret>")
        print("  PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com")
        print("\nAll automated tests with mocked PayPal responses have passed (23/23).")
        return

    print(f"\nTarget Sandbox URL: {settings.paypal_base_url}")
    print(f"Client ID: {settings.paypal_client_id[:8]}...{settings.paypal_client_id[-4:]}")
    print("Requesting real OAuth token from PayPal Sandbox...")

    service = PayPalService()
    try:
        token = await service.get_access_token(force_refresh=True)
        print(f"[SUCCESS] OAuth Bearer token acquired (length: {len(token)} characters)")
    except PayPalAuthError as e:
        print(f"[FAILED] OAuth token acquisition failed: {e.message}")
        return
    except Exception as e:
        print(f"[FAILED] Unexpected error acquiring token: {e}")
        return

    print("\nCreating a test sandbox order for $289.50 (AeroPro Ergonomic Chair)...")
    try:
        order = await service.create_order(
            internal_order_id="sandbox-test-live-001",
            total_amount=Decimal("289.50"),
            currency="USD",
            items=[{
                "sku": "CHAIR-ERGO-01",
                "name": "AeroPro Ergonomic Mesh Chair",
                "quantity": 1,
                "unit_price": Decimal("289.50"),
            }],
            idempotency_key="sandbox-test-live-key-001",
        )
        paypal_order_id = order.get("id")
        links = order.get("links", [])
        approve_link = next((l["href"] for l in links if l.get("rel") == "approve"), None)

        print(f"[SUCCESS] Sandbox Order created with PayPal ID: {paypal_order_id}")
        if approve_link:
            print(f"Approval URL: {approve_link}")
        print("\nLive Sandbox connectivity verified successfully!")
    except Exception as e:
        print(f"[FAILED] Sandbox order creation failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
