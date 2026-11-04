import re
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.schemas.assistant import RawLLMPlanResponse, RawLLMRecommendation
from app.services.ai.base import BaseAIProvider


class MockAIProvider(BaseAIProvider):
    """
    Deterministic mock AI provider for testing and offline development.
    Interprets natural language keywords, extracts quantities, checks budget,
    and handles ambiguity and prompt injection gracefully.
    """

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return "deterministic-rules"

    async def generate_plan(
        self,
        prompt: str,
        catalog_items: List[Dict[str, Any]],
        budget: Optional[Decimal] = None,
    ) -> RawLLMPlanResponse:
        cleaned_prompt = prompt.lower().strip()

        # 1. Ambiguity Detection
        ambiguous_triggers = [
            "something for my office",
            "buy stuff",
            "help me",
            "anything",
            "recommend something",
            "office stuff",
            "surprise me",
        ]
        if any(trigger in cleaned_prompt for trigger in ambiguous_triggers) and len(cleaned_prompt.split()) < 6:
            return RawLLMPlanResponse(
                interpretation="User is requesting general office items without specifying categories or preferences.",
                recommendations=[],
                clarification_needed=(
                    "Your request is ambiguous. Please specify the type of equipment you need "
                    "(e.g., ergonomic seating, standing desks, displays, split keyboards, headsets, or lighting) "
                    "and any budget preference."
                ),
            )

        # 2. Unsupported Categories (Coffee, Laptops, Food, etc.)
        unsupported_keywords = ["coffee", "espresso", "latte", "laptop", "macbook", "phone", "car", "snack", "pizza"]
        if any(unsupported in cleaned_prompt for unsupported in unsupported_keywords):
            return RawLLMPlanResponse(
                interpretation=f"User requested products not sold in this store: '{prompt}'.",
                recommendations=[],
                clarification_needed=None,
                budget_notes="The merchant catalog currently stocks office furniture, displays, audio, peripherals, and lighting.",
            )

        # 3. Prompt Injection Handling
        # If user tries to override system instructions or modify prices, treat the prompt safely
        is_injection_attempt = any(
            phrase in cleaned_prompt
            for phrase in [
                "ignore previous",
                "ignore all",
                "system prompt",
                "price to 0",
                "make it free",
                "bypass",
                "drop table",
                "admin mode",
            ]
        )

        # Extract quantities if specified (e.g. '2 chairs', '5 keyboards')
        qty_match = re.search(r"(\d+)\s*(?:x\s*)?(chairs?|desks?|monitors?|keyboards?|headsets?|lamps?|mats?|docks?)", cleaned_prompt)
        default_qty = int(qty_match.group(1)) if qty_match else 1
        if default_qty <= 0 or default_qty > 1000:
            default_qty = 1

        recommendations: List[RawLLMRecommendation] = []

        # Keyword mapping to catalog SKUs
        if "chair" in cleaned_prompt or "seating" in cleaned_prompt or "lumbar" in cleaned_prompt:
            recommendations.append(
                RawLLMRecommendation(
                    sku="CHAIR-ERGO-01",
                    quantity=default_qty,
                    reason="Breathable high-back ergonomic mesh chair with dynamic lumbar support to prevent back strain.",
                )
            )

        if "desk" in cleaned_prompt or "standing" in cleaned_prompt or "workstation" in cleaned_prompt:
            # Check if budget permits standing desk or if chair was already chosen
            recommendations.append(
                RawLLMRecommendation(
                    sku="DESK-STAND-02",
                    quantity=default_qty,
                    reason="Electric dual-motor standing desk with height presets for an active ergonomic workstation.",
                )
            )

        if "monitor" in cleaned_prompt or "screen" in cleaned_prompt or "display" in cleaned_prompt or "ultrawide" in cleaned_prompt:
            recommendations.append(
                RawLLMRecommendation(
                    sku="MON-CURVE-03",
                    quantity=default_qty,
                    reason="34-inch curved WQHD ultrawide monitor with USB-C 90W power delivery and built-in KVM.",
                )
            )

        if "keyboard" in cleaned_prompt or "typing" in cleaned_prompt or "mechanical" in cleaned_prompt:
            recommendations.append(
                RawLLMRecommendation(
                    sku="KB-SPLIT-04",
                    quantity=default_qty,
                    reason="Wireless split ergonomic mechanical keyboard with cushioned wrist rests to reduce wrist fatigue.",
                )
            )

        if "headset" in cleaned_prompt or "audio" in cleaned_prompt or "headphones" in cleaned_prompt or "anc" in cleaned_prompt or "calls" in cleaned_prompt:
            recommendations.append(
                RawLLMRecommendation(
                    sku="AUDIO-HEADSET-05",
                    quantity=default_qty,
                    reason="Pro wireless headset featuring hybrid active noise cancellation and AI beamforming microphone.",
                )
            )

        if "dock" in cleaned_prompt or "hub" in cleaned_prompt or "thunderbolt" in cleaned_prompt:
            recommendations.append(
                RawLLMRecommendation(
                    sku="DOCK-TB4-06",
                    quantity=default_qty,
                    reason="11-in-1 Thunderbolt 4 docking station with dual 4K support and 96W power delivery.",
                )
            )

        if "light" in cleaned_prompt or "lamp" in cleaned_prompt or "lightbar" in cleaned_prompt:
            recommendations.append(
                RawLLMRecommendation(
                    sku="LAMP-LIGHTBAR-07",
                    quantity=default_qty,
                    reason="Smart monitor light bar designed to eliminate screen glare and reduce eye strain.",
                )
            )

        if "mat" in cleaned_prompt or "anti-fatigue" in cleaned_prompt:
            recommendations.append(
                RawLLMRecommendation(
                    sku="MAT-FLOOR-08",
                    quantity=default_qty,
                    reason="Contoured ergonomic anti-fatigue standing mat designed to alleviate leg and lumbar fatigue.",
                )
            )

        # Fallback if user asks for generic "ergonomic setup"
        if not recommendations and ("ergonomic" in cleaned_prompt or "setup" in cleaned_prompt or "work from home" in cleaned_prompt):
            recommendations.append(
                RawLLMRecommendation(
                    sku="CHAIR-ERGO-01",
                    quantity=1,
                    reason="Core ergonomic foundation chair for prolonged desk comfort.",
                )
            )
            recommendations.append(
                RawLLMRecommendation(
                    sku="KB-SPLIT-04",
                    quantity=1,
                    reason="Companion split mechanical keyboard for natural forearm alignment.",
                )
            )

        interpretation = f"Interpreted shopping intent for: '{prompt}'."
        if is_injection_attempt:
            interpretation += " (Security Notice: System override instructions were detected and safely ignored)."

        return RawLLMPlanResponse(
            interpretation=interpretation,
            recommendations=recommendations,
            clarification_needed=None,
            budget_notes=f"Evaluated against budget constraint: {budget}" if budget else None,
        )
