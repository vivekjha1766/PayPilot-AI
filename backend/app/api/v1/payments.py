from fastapi import APIRouter
from app.core.config import settings
from app.schemas.order import PaymentConfigResponse

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/config", response_model=PaymentConfigResponse)
async def get_payment_config() -> PaymentConfigResponse:
    """
    Returns public PayPal client configuration.
    Security guarantee: NEVER exposes the client secret.
    """
    return PaymentConfigResponse(
        client_id=settings.paypal_client_id,
        currency=settings.paypal_currency,
        is_configured=settings.is_paypal_configured,
        sandbox=True,
    )
