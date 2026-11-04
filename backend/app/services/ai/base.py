from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List, Optional
from app.schemas.assistant import RawLLMPlanResponse


class BaseAIProvider(ABC):
    """
    Provider-independent AI Service interface for generating catalog-grounded purchase plans.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'gemini', 'mock')."""
        pass

    @abstractmethod
    async def generate_plan(
        self,
        prompt: str,
        catalog_items: List[Dict[str, Any]],
        budget: Optional[Decimal] = None,
    ) -> RawLLMPlanResponse:
        """
        Parses user intent and returns raw LLM recommendations referencing catalog items.
        Model output must be treated as untrusted and validated by the caller.
        """
        pass


# Alias for backwards compatibility
AIService = BaseAIProvider
