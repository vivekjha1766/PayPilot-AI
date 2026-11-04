import uuid
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.catalog import CatalogItem
from app.models.order import Order
from app.schemas.assistant import (
    AssistantPlanRequest,
    AssistantPlanResponse,
    BudgetStatus,
    GroundedRecommendation,
)
from app.services.ai.factory import AIUnconfiguredError, get_ai_provider
from app.services.risk_service import RiskAssessmentService


class AssistantService:
    @classmethod
    async def create_plan(
        cls,
        request: AssistantPlanRequest,
        db: AsyncSession,
        provider_name: Optional[str] = None,
    ) -> AssistantPlanResponse:
        """
        Creates a catalog-grounded purchasing plan from natural language.
        Strict server-side validation guarantees:
        - All SKUs must exist in the real database catalog.
        - All unit prices and stock counts are retrieved authoritatively from the database.
        - Quantities are constrained to warehouse availability.
        - Totals and budget comparisons are calculated with Decimal precision.
        - Model output is treated as untrusted.
        """
        plan_id = str(uuid.uuid4())
        warnings: List[str] = []

        # 1. Fetch Authoritative Catalog from SQLite Database
        stmt = select(CatalogItem)
        result = await db.execute(stmt)
        catalog_items = list(result.scalars().all())
        catalog_map = {item.sku: item for item in catalog_items}

        catalog_context = [
            {
                "sku": item.sku,
                "name": item.name,
                "category": item.category,
                "description": item.description,
                "unit_price": item.unit_price,
                "stock": item.stock,
            }
            for item in catalog_items
        ]

        # 2. Retrieve AI Provider
        try:
            ai_provider = get_ai_provider(provider_name=provider_name)
        except AIUnconfiguredError as e:
            # Clear, actionable unconfigured state — does not pretend to be live AI
            risk = RiskAssessmentService.evaluate_plan_risk(
                user_prompt=request.prompt,
                grounded_items=[],
                subtotal=Decimal("0.00"),
                currency=settings.paypal_currency,
                budget=request.budget,
            )
            return AssistantPlanResponse(
                plan_id=plan_id,
                intent_interpretation="Live Gemini AI provider is not currently configured.",
                recommendations=[],
                subtotal="0.00",
                currency=settings.paypal_currency,
                budget=f"{request.budget:.2f}" if request.budget is not None else None,
                budget_status=BudgetStatus.NO_BUDGET_SPECIFIED if request.budget is None else BudgetStatus.WITHIN_BUDGET,
                clarification_needed=None,
                warnings=[str(e)],
                risk_assessment=risk,
                is_actionable=False,
                ai_provider="unconfigured",
                model_name=None,
            )

        # 3. Request LLM Intent Parsing
        raw_plan = await ai_provider.generate_plan(
            prompt=request.prompt,
            catalog_items=catalog_context,
            budget=request.budget,
        )

        # 4. Authoritative Catalog Grounding & Resolution
        grounded_recs: List[GroundedRecommendation] = []
        grounded_for_risk: List[dict] = []
        subtotal = Decimal("0.00")

        for raw_rec in raw_plan.recommendations:
            clean_sku = raw_rec.sku.strip()
            cat_item = catalog_map.get(clean_sku)

            if not cat_item:
                warnings.append(
                    f"Model suggested SKU '{clean_sku}' which does not exist in authoritative catalog; discarded."
                )
                continue

            # Validate and constrain quantities
            req_qty = raw_rec.quantity
            if req_qty <= 0:
                warnings.append(f"Invalid quantity ({req_qty}) requested for '{cat_item.name}'; adjusted to 1.")
                req_qty = 1

            avail_stock = cat_item.stock
            if req_qty > avail_stock:
                rec_qty = max(0, avail_stock)
                warnings.append(
                    f"Requested quantity {req_qty} for '{cat_item.name}' exceeds available warehouse stock ({avail_stock}). Adjusted recommendation to {rec_qty}."
                )
            else:
                rec_qty = req_qty

            unit_price = Decimal(str(cat_item.unit_price))
            line_total = unit_price * Decimal(rec_qty)
            subtotal += line_total

            grounded_recs.append(
                GroundedRecommendation(
                    catalog_item_id=cat_item.id,
                    sku=cat_item.sku,
                    name=cat_item.name,
                    category=cat_item.category,
                    requested_quantity=req_qty,
                    recommended_quantity=rec_qty,
                    unit_price=f"{unit_price:.2f}",
                    total_price=f"{line_total:.2f}",
                    in_stock=(avail_stock > 0 and rec_qty > 0),
                    stock_available=avail_stock,
                    reason=raw_rec.reason or f"Recommended based on request for {cat_item.category.lower()}.",
                )
            )

            grounded_for_risk.append({
                "sku": cat_item.sku,
                "requested_quantity": req_qty,
                "recommended_quantity": rec_qty,
                "unit_price": unit_price,
                "stock_available": avail_stock,
            })

        # 5. Authoritative Budget Evaluation
        budget_str = f"{request.budget:.2f}" if request.budget is not None else None
        budget_diff_str: Optional[str] = None

        if request.budget is not None:
            if subtotal <= request.budget:
                budget_status = BudgetStatus.WITHIN_BUDGET
                budget_diff = request.budget - subtotal
                budget_diff_str = f"{budget_diff:.2f}"
            else:
                budget_status = BudgetStatus.EXCEEDS_BUDGET
                budget_diff = subtotal - request.budget
                budget_diff_str = f"{budget_diff:.2f}"
                warnings.append(
                    f"Authoritative plan subtotal (${subtotal:.2f}) exceeds specified budget (${request.budget:.2f}) by ${budget_diff:.2f}."
                )
        else:
            budget_status = BudgetStatus.NO_BUDGET_SPECIFIED

        # 6. Fetch Recent Orders for Velocity / Duplicate Risk Analysis
        recent_stmt = select(Order).order_by(Order.created_at.desc()).limit(5)
        recent_res = await db.execute(recent_stmt)
        recent_orders = list(recent_res.scalars().all())

        # 7. Evaluate Explainable Transaction Risk
        risk_assessment = RiskAssessmentService.evaluate_plan_risk(
            user_prompt=request.prompt,
            grounded_items=grounded_for_risk,
            subtotal=subtotal,
            currency=settings.paypal_currency,
            budget=request.budget,
            recent_orders=recent_orders,
        )

        is_actionable = (
            len(grounded_recs) > 0
            and raw_plan.clarification_needed is None
            and any(rec.recommended_quantity > 0 for rec in grounded_recs)
        )

        fallback_used = getattr(ai_provider, "fallback_used", False)
        fallback_model = getattr(ai_provider, "fallback_model", None)
        if fallback_used:
            warnings.append(
                f"Notice: Primary model experienced transient upstream capacity pressure. Recommendations were successfully generated via resilient fallback model '{ai_provider.model}'."
            )

        return AssistantPlanResponse(
            plan_id=plan_id,
            intent_interpretation=raw_plan.interpretation,
            recommendations=grounded_recs,
            subtotal=f"{subtotal:.2f}",
            currency=settings.paypal_currency,
            budget=budget_str,
            budget_status=budget_status,
            budget_difference=budget_diff_str,
            clarification_needed=raw_plan.clarification_needed,
            warnings=warnings,
            risk_assessment=risk_assessment,
            is_actionable=is_actionable,
            ai_provider=ai_provider.provider_name,
            model_name=ai_provider.model if hasattr(ai_provider, "model") else None,
            fallback_used=fallback_used,
            fallback_model=fallback_model if fallback_used else None,
        )
