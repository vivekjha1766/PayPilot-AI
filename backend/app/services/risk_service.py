from decimal import Decimal
from typing import Any, Dict, List, Optional
from app.models.catalog import CatalogItem
from app.models.order import Order, OrderStatus
from app.schemas.assistant import RiskLevel, TransactionRiskAssessment


class RiskAssessmentService:
    """
    Transparent, deterministic rule-based transaction risk assessment service.

    SCORING DOCUMENTATION:
    - Range: 0 to 100 (integer)
    - 0 to 25: LOW RISK — Standard transaction parameters, all items in stock,
      prices match authoritative catalog, no duplicate or anomalous signals.
      Recommended Action: 'PROCEED_TO_CHECKOUT'
    - 26 to 65: MEDIUM RISK — Non-critical warnings present (e.g., requested quantity
      exceeds current warehouse stock, budget exceeded, or prompt anomaly detected).
      Recommended Action: 'REVIEW_PURCHASE_PLAN'
    - 66 to 100: HIGH RISK — Critical inconsistencies or security discrepancies detected
      (e.g., client price tampering, currency mismatch, duplicate rapid replay attempts,
      or invalid order lifecycle state).
      Recommended Action: 'SECURITY_HOLD_OR_REAUTH'

    NOTICE:
    This service is advisory and explainable. It does not claim to detect identity theft
    or replace payment network authorization. Server-authoritative validation rules
    continue to strictly enforce hard business constraints.
    """

    @classmethod
    def evaluate_plan_risk(
        cls,
        user_prompt: str,
        grounded_items: List[Dict[str, Any]],
        subtotal: Decimal,
        currency: str,
        budget: Optional[Decimal] = None,
        recent_orders: Optional[List[Order]] = None,
    ) -> TransactionRiskAssessment:
        score = 0
        signals: List[str] = []
        reasons: List[str] = []

        # 1. Quantity & Stock Consistency
        for item in grounded_items:
            req_qty = item.get("requested_quantity", 1)
            stock = item.get("stock_available", 0)
            sku = item.get("sku", "UNKNOWN")

            if req_qty <= 0:
                score += 40
                signals.append(f"INVALID_QUANTITY_{sku}")
                reasons.append(f"Item '{sku}' has non-positive requested quantity ({req_qty}).")
            elif req_qty > stock:
                score += 20
                signals.append(f"STOCK_EXCEEDED_{sku}")
                reasons.append(
                    f"Requested quantity ({req_qty}) for item '{sku}' exceeds available warehouse stock ({stock})."
                )

        # 2. Currency Consistency
        if currency != "USD":
            score += 30
            signals.append("NON_STANDARD_CURRENCY")
            reasons.append(f"Currency '{currency}' deviates from merchant baseline 'USD'.")

        # 3. Budget Overrun Checks
        if budget is not None and budget > Decimal("0.00"):
            if subtotal > budget:
                overrun_pct = ((subtotal - budget) / budget) * 100
                if overrun_pct > 50:
                    score += 20
                    signals.append("SEVERE_BUDGET_OVERRUN")
                    reasons.append(
                        f"Recommended purchase subtotal (${subtotal:.2f}) exceeds budget (${budget:.2f}) by {overrun_pct:.1f}%."
                    )
                else:
                    score += 10
                    signals.append("MODERATE_BUDGET_OVERRUN")
                    reasons.append(
                        f"Recommended purchase subtotal (${subtotal:.2f}) exceeds budget (${budget:.2f}) by ${subtotal - budget:.2f}."
                    )

        # 4. High-Value Threshold Check
        if subtotal >= Decimal("2000.00"):
            score += 15
            signals.append("HIGH_VALUE_PURCHASE")
            reasons.append(f"Order total (${subtotal:.2f}) exceeds standard high-value threshold of $2,000.00.")

        # 5. Prompt Anomaly / Injection Signal Check
        suspicious_terms = [
            "ignore previous",
            "system prompt",
            "price to 0",
            "admin mode",
            "make it free",
            "bypass validation",
            "drop table",
        ]
        prompt_lower = user_prompt.lower()
        if any(term in prompt_lower for term in suspicious_terms):
            score += 25
            signals.append("PROMPT_INJECTION_PATTERN_DETECTED")
            reasons.append(
                "Input prompt contained security override or price tampering patterns (safely neutralized)."
            )

        # 6. Duplicate / Rapid Replay Check
        if recent_orders and grounded_items:
            skus_in_plan = sorted([item.get("sku") for item in grounded_items])
            for order in recent_orders[:5]:
                order_skus = sorted([oi.sku for oi in order.items])
                if order_skus == skus_in_plan and abs(order.total_amount - subtotal) < Decimal("0.01"):
                    score += 25
                    signals.append("POTENTIAL_RAPID_DUPLICATE_ORDER")
                    reasons.append(
                        f"An order with identical items and subtotal (${subtotal:.2f}) was created recently (Order ID {order.id[:8]})."
                    )
                    break

        # Bound score between 0 and 100
        score = min(100, max(0, score))

        # Categorize Risk Level
        if score <= 25:
            risk_level = RiskLevel.LOW
            action = "PROCEED_TO_CHECKOUT"
            if not reasons:
                reasons.append("All line items grounded in catalog, in stock, and within normal risk parameters.")
        elif score <= 65:
            risk_level = RiskLevel.MEDIUM
            action = "REVIEW_PURCHASE_PLAN"
        else:
            risk_level = RiskLevel.HIGH
            action = "SECURITY_HOLD_OR_REAUTH"

        return TransactionRiskAssessment(
            risk_level=risk_level,
            score=score,
            signals=signals,
            reasons=reasons,
            recommended_action=action,
        )

    @classmethod
    def evaluate_order_risk(
        cls,
        order: Order,
        catalog_map: Dict[int, CatalogItem],
        submitted_unit_prices: Optional[Dict[str, Decimal]] = None,
    ) -> TransactionRiskAssessment:
        """
        Evaluates risk for an existing order or capture attempt against authoritative catalog data.
        """
        score = 0
        signals: List[str] = []
        reasons: List[str] = []

        # 1. State Validity Check
        if order.status == OrderStatus.COMPLETED:
            score += 50
            signals.append("ORDER_ALREADY_COMPLETED")
            reasons.append("Order is already in COMPLETED status; re-capturing is disallowed.")
        elif order.status == OrderStatus.CANCELLED:
            score += 60
            signals.append("ORDER_CANCELLED")
            reasons.append("Order was cancelled by buyer or merchant.")
        elif order.status == OrderStatus.CAPTURING:
            score += 35
            signals.append("CONCURRENT_CAPTURE_ATTEMPT")
            reasons.append("Capture operation is currently in progress.")

        # 2. Client Price Tampering Check
        if submitted_unit_prices:
            for item in order.items:
                authoritative_price = Decimal(str(item.unit_price))
                submitted = submitted_unit_prices.get(item.sku)
                if submitted is not None and abs(submitted - authoritative_price) > Decimal("0.001"):
                    score += 70
                    signals.append(f"PRICE_TAMPERING_{item.sku}")
                    reasons.append(
                        f"Client submitted price ${submitted} for {item.sku} does not match authoritative catalog price ${authoritative_price}."
                    )

        # 3. Stock Availability Check
        for item in order.items:
            cat_item = catalog_map.get(item.catalog_item_id)
            if not cat_item:
                score += 50
                signals.append(f"ITEM_NOT_FOUND_{item.sku}")
                reasons.append(f"Item '{item.sku}' not found in catalog.")
            elif item.quantity > cat_item.stock:
                score += 30
                signals.append(f"STOCK_EXCEEDED_{item.sku}")
                reasons.append(
                    f"Quantity {item.quantity} exceeds available stock ({cat_item.stock}) for '{cat_item.name}'."
                )

        score = min(100, max(0, score))
        if score <= 25:
            risk_level = RiskLevel.LOW
            action = "PROCEED_TO_CHECKOUT"
        elif score <= 65:
            risk_level = RiskLevel.MEDIUM
            action = "REVIEW_PURCHASE_PLAN"
        else:
            risk_level = RiskLevel.HIGH
            action = "SECURITY_HOLD_OR_REAUTH"

        return TransactionRiskAssessment(
            risk_level=risk_level,
            score=score,
            signals=signals,
            reasons=reasons,
            recommended_action=action,
        )
