from typing import Optional
from app.core.config import settings
from app.services.ai.base import BaseAIProvider
from app.services.ai.gemini_provider import GeminiAIProvider
from app.services.ai.mock_provider import MockAIProvider


from app.services.ai.exceptions import (
    AIProviderError,
    AIUnconfiguredError,
    AITimeoutError,
    AIModelNotFoundError,
    AIPermissionError,
    AIQuotaExceededError,
    AIMalformedOutputError,
    AIProviderUnavailableError,
)


_CUSTOM_PROVIDERS: dict = {}


def register_provider(name: str, provider: BaseAIProvider) -> None:
    _CUSTOM_PROVIDERS[name] = provider


def get_ai_provider(provider_name: Optional[str] = None) -> BaseAIProvider:
    """
    Factory to retrieve the appropriate AI provider.
    - If registered in _CUSTOM_PROVIDERS, returns that provider.
    - If provider_name is explicitly 'mock', returns MockAIProvider.
    - If provider_name is explicitly 'gemini' or None:
      - If settings.is_gemini_configured is True, returns GeminiAIProvider.
      - If settings.is_gemini_configured is False and provider_name is None,
        raises AIUnconfiguredError so callers know live Gemini is not configured.
    """
    if provider_name in _CUSTOM_PROVIDERS:
        return _CUSTOM_PROVIDERS[provider_name]

    if provider_name == "mock":
        return MockAIProvider()

    if settings.is_gemini_configured:
        return GeminiAIProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            fallback_model=settings.gemini_fallback_model,
        )

    if provider_name == "gemini" or provider_name is None:
        raise AIUnconfiguredError(
            "Gemini AI provider is not configured. "
            "Please configure GEMINI_API_KEY in backend/.env to enable live AI assistance, "
            "or specify provider='mock' for deterministic testing."
        )

    raise ValueError(f"Unknown AI provider requested: {provider_name}")
