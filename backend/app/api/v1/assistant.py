import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.assistant import AssistantPlanRequest, AssistantPlanResponse
from app.services.ai.factory import (
    AIProviderError,
    AIUnconfiguredError,
    AITimeoutError,
    AIModelNotFoundError,
    AIPermissionError,
    AIQuotaExceededError,
    AIMalformedOutputError,
    AIProviderUnavailableError,
)
from app.services.assistant_service import AssistantService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["Assistant"])


class AssistantStatusResponse(BaseModel):
    is_configured: bool
    default_provider: str
    supported_providers: list[str]
    configured_model: Optional[str] = None
    fallback_model: Optional[str] = None


@router.get("/status", response_model=AssistantStatusResponse)
async def get_assistant_status() -> AssistantStatusResponse:
    """
    Returns the operational configuration of the AI Purchasing Assistant.
    Security guarantee: NEVER exposes API keys.
    """
    return AssistantStatusResponse(
        is_configured=settings.is_gemini_configured,
        default_provider="gemini" if settings.is_gemini_configured else "unconfigured",
        supported_providers=["gemini", "mock"],
        configured_model=settings.gemini_model if settings.is_gemini_configured else None,
        fallback_model=settings.gemini_fallback_model if settings.is_gemini_configured else None,
    )


@router.post("/plan", response_model=AssistantPlanResponse, status_code=status.HTTP_200_OK)
async def create_purchasing_plan(
    payload: AssistantPlanRequest,
    provider: Optional[str] = Query(
        None,
        description="Optional provider override ('mock' or 'gemini'). Defaults to live Gemini if configured.",
    ),
    db: AsyncSession = Depends(get_db),
) -> AssistantPlanResponse:
    """
    Converts a natural-language purchasing request into an explainable,
    catalog-grounded purchase plan with transparent risk scoring.
    """
    try:
        plan = await asyncio.wait_for(
            AssistantService.create_plan(
                request=payload,
                db=db,
                provider_name=provider,
            ),
            timeout=20.0,
        )
        return plan
    except AIUnconfiguredError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.sanitized_message,
        )
    except AIModelNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=e.sanitized_message,
        )
    except AIPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=e.sanitized_message,
        )
    except AIQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.sanitized_message,
        )
    except AIMalformedOutputError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=e.sanitized_message,
        )
    except AIProviderUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.sanitized_message,
        )
    except AITimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=e.sanitized_message,
        )
    except asyncio.TimeoutError:
        logger.error("AI purchasing assistant request timed out after 20.0s")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI purchasing assistant timed out while generating recommendations. Please try again.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to generate purchasing plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI assistant service encountered an error while processing your plan. Direct catalog checkout is still available.",
        )

