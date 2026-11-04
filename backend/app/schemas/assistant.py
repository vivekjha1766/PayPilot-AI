from decimal import Decimal
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class BudgetStatus(str, Enum):
    WITHIN_BUDGET = "WITHIN_BUDGET"
    EXCEEDS_BUDGET = "EXCEEDS_BUDGET"
    NO_BUDGET_SPECIFIED = "NO_BUDGET_SPECIFIED"


class AssistantPlanRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language purchasing request or shopping requirement.",
    )
    budget: Optional[Decimal] = Field(
        default=None,
        ge=Decimal("0.00"),
        description="Optional customer spending limit in target currency.",
    )
    context: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional additional context (e.g., home office, team size).",
    )


class RawLLMRecommendation(BaseModel):
    sku: str
    quantity: int = 1
    reason: str


class RawLLMPlanResponse(BaseModel):
    interpretation: str
    recommendations: List[RawLLMRecommendation] = Field(default_factory=list)
    clarification_needed: Optional[str] = None
    budget_notes: Optional[str] = None


class GroundedRecommendation(BaseModel):
    catalog_item_id: int
    sku: str
    name: str
    category: str
    requested_quantity: int
    recommended_quantity: int
    unit_price: str
    total_price: str
    in_stock: bool
    stock_available: int
    reason: str

    model_config = ConfigDict(from_attributes=True)


class TransactionRiskAssessment(BaseModel):
    risk_level: RiskLevel
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Risk score from 0 (safest) to 100 (highest risk). 0-25: LOW, 26-65: MEDIUM, 66-100: HIGH.",
    )
    signals: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)
    recommended_action: str


class AssistantPlanResponse(BaseModel):
    plan_id: str
    intent_interpretation: str
    recommendations: List[GroundedRecommendation] = Field(default_factory=list)
    subtotal: str
    currency: str
    budget: Optional[str] = None
    budget_status: BudgetStatus
    budget_difference: Optional[str] = None
    clarification_needed: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    risk_assessment: TransactionRiskAssessment
    is_actionable: bool
    ai_provider: str
    model_name: Optional[str] = None
    fallback_used: bool = False
    fallback_model: Optional[str] = None
