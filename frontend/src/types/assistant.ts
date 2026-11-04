export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';

export type BudgetStatus = 'WITHIN_BUDGET' | 'EXCEEDS_BUDGET' | 'NO_BUDGET_SPECIFIED';

export interface GroundedRecommendation {
  catalog_item_id: number;
  sku: string;
  name: string;
  category: string;
  requested_quantity: number;
  recommended_quantity: number;
  unit_price: string;
  total_price: string;
  in_stock: boolean;
  stock_available: number;
  reason: string;
}

export interface TransactionRiskAssessment {
  risk_level: RiskLevel;
  score: number;
  signals: string[];
  reasons: string[];
  recommended_action: string;
}

export interface AssistantPlanResponse {
  plan_id: string;
  intent_interpretation: string;
  recommendations: GroundedRecommendation[];
  subtotal: string;
  currency: string;
  budget: string | null;
  budget_status: BudgetStatus;
  budget_difference: string | null;
  clarification_needed: string | null;
  warnings: string[];
  risk_assessment: TransactionRiskAssessment;
  is_actionable: boolean;
  ai_provider: string;
  model_name?: string | null;
  fallback_used?: boolean;
  fallback_model?: string | null;
}

export interface AssistantStatus {
  is_configured: boolean;
  default_provider: string;
  supported_providers: string[];
  configured_model?: string | null;
  fallback_model?: string | null;
}
