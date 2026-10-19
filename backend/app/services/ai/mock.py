from typing import Any, Dict
from app.services.ai.base import AIService


class MockAIService(AIService):
    """
    Deterministic test double for AIService.
    Used for unit testing, offline execution, and predictable validation.
    """

    async def parse_purchase_intent(self, prompt: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        items = []

        if "chair" in prompt_lower:
            items.append({"sku": "CHAIR-ERGO-01", "quantity": 1})
        if "desk" in prompt_lower:
            items.append({"sku": "DESK-STAND-02", "quantity": 1})
        if "monitor" in prompt_lower:
            items.append({"sku": "MON-CURVE-03", "quantity": 1})
        if "keyboard" in prompt_lower:
            items.append({"sku": "KB-SPLIT-04", "quantity": 1})

        # Default fallback if no match
        if not items:
            items.append({"sku": "CHAIR-ERGO-01", "quantity": 1})

        return {
            "confidence": 0.95,
            "raw_prompt": prompt,
            "matched_candidates": items,
            "notes": "Parsed by MockAIService deterministic double",
        }

    async def evaluate_risk(self, draft_order: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "risk_score": 10,
            "risk_level": "LOW",
            "reasons": [
                "Catalog items verified by internal merchant database",
                "Transaction within standard daily purchasing limit",
            ],
            "requires_secondary_approval": False,
        }
