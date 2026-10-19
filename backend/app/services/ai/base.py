from abc import ABC, abstractmethod
from typing import Any, Dict


class AIService(ABC):
    """
    Provider-independent interface for AI operations in PayPilot AI.
    Controls intent extraction and explainable risk analysis.
    """

    @abstractmethod
    async def parse_purchase_intent(self, prompt: str) -> Dict[str, Any]:
        """
        Parses natural language purchase intent into structured candidate items.
        Does NOT execute orders or dictate binding prices.
        """
        pass

    @abstractmethod
    async def evaluate_risk(self, draft_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates risk on server-validated draft order and returns an explainable score.
        """
        pass
