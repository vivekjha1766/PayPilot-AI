import React, { useState } from 'react';
import type { AssistantPlanResponse, GroundedRecommendation } from '../types/assistant';
import { generateAssistantPlan } from '../services/api';
import {
  Send,
  Loader2,
  AlertCircle,
  HelpCircle,
  ShieldCheck,
  ShieldAlert,
  Shield,
  Plus,
  Check,
  Info,
} from 'lucide-react';

interface AIPurchasingAssistantProps {
  onAddItemsToCart: (items: { sku: string; quantity: number }[]) => void;
  onOpenCart: () => void;
  isConfigured: boolean;
  configuredModel?: string | null;
  fallbackModel?: string | null;
}

const EXAMPLE_PROMPTS = [
  'Equip an ergonomic workstation with a chair and split keyboard under $500',
  'I need a curved ultrawide monitor and thunderbolt dock for programming',
  'Noise cancelling headset and smart light bar for remote meetings',
  'AeroPro ergonomic chair and anti-fatigue floor mat',
];

export const AIPurchasingAssistant: React.FC<AIPurchasingAssistantProps> = ({
  onAddItemsToCart,
  onOpenCart,
  isConfigured,
  configuredModel,
  fallbackModel,
}) => {
  const [prompt, setPrompt] = useState<string>('');
  const [budgetInput, setBudgetInput] = useState<string>('');
  const [useMock, setUseMock] = useState<boolean>(!isConfigured);
  const [hasManuallyToggled, setHasManuallyToggled] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [plan, setPlan] = useState<AssistantPlanResponse | null>(null);
  const [addedSuccess, setAddedSuccess] = useState<boolean>(false);

  React.useEffect(() => {
    if (!hasManuallyToggled) {
      setUseMock(!isConfigured);
    }
  }, [isConfigured, hasManuallyToggled]);

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const initialPrompt = params.get('prompt');
    const autoRun = params.get('auto') === 'true';
    if (initialPrompt) {
      setPrompt(initialPrompt);
      if (params.get('budget')) {
        setBudgetInput(params.get('budget')!);
      }
      if (autoRun) {
        const budgetNum = params.get('budget') ? parseFloat(params.get('budget')!) : undefined;
        setLoading(true);
        generateAssistantPlan(initialPrompt, budgetNum, params.get('provider') || undefined)
          .then((res) => setPlan(res))
          .catch((err) => setError(err instanceof Error ? err.message : 'Error'))
          .finally(() => setLoading(false));
      }
    }
  }, []);

  const handleSubmit = async (e?: React.FormEvent, customPrompt?: string) => {
    if (e) e.preventDefault();
    const queryText = (customPrompt || prompt).trim();
    if (!queryText) return;

    setLoading(true);
    setError(null);
    setAddedSuccess(false);

    try {
      const budgetNum = budgetInput ? parseFloat(budgetInput) : undefined;
      const providerParam = useMock ? 'mock' : undefined;
      const result = await generateAssistantPlan(queryText, budgetNum, providerParam);
      setPlan(result);
      if (customPrompt) setPrompt(customPrompt);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate purchasing plan');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyToCart = () => {
    if (!plan || !plan.recommendations.length) return;

    const itemsToAdd = plan.recommendations
      .filter((rec) => rec.recommended_quantity > 0)
      .map((rec) => ({
        sku: rec.sku,
        quantity: rec.recommended_quantity,
      }));

    if (itemsToAdd.length > 0) {
      onAddItemsToCart(itemsToAdd);
      setAddedSuccess(true);
      setTimeout(() => {
        onOpenCart();
      }, 500);
    }
  };

  const getRiskBadge = (level: string, score: number) => {
    if (level === 'LOW') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-accent-forest-bg text-accent-forest border border-accent-forest-border font-medium">
          <ShieldCheck className="w-3 h-3" />
          LOW RISK ({score}/100)
        </span>
      );
    }
    if (level === 'MEDIUM') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-accent-amber-bg text-accent-amber border border-accent-amber-border font-medium">
          <Shield className="w-3 h-3" />
          MEDIUM RISK ({score}/100)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-accent-crimson-bg text-accent-crimson border border-accent-crimson-border font-medium">
        <ShieldAlert className="w-3 h-3" />
        HIGH RISK ({score}/100)
      </span>
    );
  };

  return (
    <section className="bg-white rounded border border-slate-border p-6 sm:p-8 space-y-6 shadow-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-5 border-b border-slate-line">
        <div>
          <div className="flex items-baseline gap-2.5">
            <h2 className="font-serif text-xl sm:text-2xl text-navy font-normal tracking-tight">
              Purchasing Consultant
            </h2>
            <span className="text-[10px] font-mono uppercase tracking-widest text-blue-primary font-medium">
              Advisory
            </span>
          </div>
          <p className="text-xs text-slate-muted mt-1 leading-relaxed">
            Intent parsing strictly grounded in warehouse catalog inventory and authoritative unit pricing.
          </p>
        </div>

        {/* Mode & Provider Status */}
        <div className="flex items-center gap-3 text-xs self-end sm:self-auto">
          <span className="px-2.5 py-1 rounded border border-blue-border bg-blue-soft text-[11px] font-mono text-blue-dark">
            {useMock
              ? 'Provider: Mock (Deterministic Rules)'
              : isConfigured
              ? `Provider: Gemini (${configuredModel || '3.8 Flash'}${fallbackModel ? ` | Fallback: ${fallbackModel}` : ''})`
              : 'Provider: Key Unconfigured'}
          </span>

          <label className="flex items-center gap-1.5 cursor-pointer text-slate-muted hover:text-navy text-[11px]" title="Toggle deterministic test mock versus live Gemini API">
            <input
              type="checkbox"
              checked={useMock}
              onChange={(e) => {
                setHasManuallyToggled(true);
                setUseMock(e.target.checked);
              }}
              className="rounded border-slate-border text-blue-primary focus:ring-0 focus:outline-none"
            />
            <span className="font-sans">Test Mode (Mock)</span>
          </label>
        </div>
      </div>

      {/* Query Form */}
      <form onSubmit={(e) => handleSubmit(e)} className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1">
            <label htmlFor="assistant-prompt" className="sr-only">
              Procurement Request
            </label>
            <input
              id="assistant-prompt"
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Equip an ergonomic workstation with chair and split keyboard under $500..."
              className="w-full px-4 py-2.5 rounded border border-slate-border bg-canvas text-xs sm:text-sm text-navy placeholder-slate-muted focus:border-blue-primary focus:bg-white transition-colors"
              disabled={loading}
            />
          </div>

          <div className="w-full sm:w-40 relative">
            <label htmlFor="assistant-budget" className="sr-only">
              Budget in USD
            </label>
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs font-mono text-slate-muted">
              $
            </span>
            <input
              id="assistant-budget"
              type="number"
              step="0.01"
              min="0"
              value={budgetInput}
              onChange={(e) => setBudgetInput(e.target.value)}
              placeholder="Budget"
              className="w-full pl-7 pr-3 py-2.5 rounded border border-slate-border bg-canvas text-xs sm:text-sm text-navy placeholder-slate-muted focus:border-blue-primary focus:bg-white transition-colors"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !prompt.trim()}
            className="px-5 py-2.5 rounded bg-blue-primary hover:bg-blue-hover disabled:opacity-40 text-white text-xs font-medium flex items-center justify-center gap-1.5 transition-colors shrink-0 shadow-xs"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Evaluating...</span>
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>Consult</span>
              </>
            )}
          </button>
        </div>

        {/* Suggestion Chips */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <span className="text-slate-muted shrink-0 text-[11px] font-mono">Suggestions:</span>
          {EXAMPLE_PROMPTS.map((ex, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSubmit(undefined, ex)}
              disabled={loading}
              className="px-2.5 py-1 rounded border border-slate-border bg-white hover:bg-blue-soft hover:border-blue-border hover:text-blue-primary text-slate-muted text-[11px] whitespace-nowrap transition-colors"
            >
              {ex}
            </button>
          ))}
        </div>
      </form>

      {/* Error Notice */}
      {error && (
        <div className="rounded p-4 bg-accent-crimson-bg border border-accent-crimson-border flex items-start gap-2.5 text-xs text-accent-crimson">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-semibold block">Consultant Evaluation Notice</span>
            <p className="mt-0.5 leading-relaxed">{error}</p>
          </div>
        </div>
      )}

      {/* Generated Purchasing Proposal */}
      {plan && (
        <div className="space-y-5 pt-4 border-t border-slate-line">
          {/* Interpreted Intent */}
          <div className="p-4 rounded border border-blue-border/70 bg-blue-soft/30 space-y-2">
            <div className="flex items-baseline justify-between text-xs text-slate-muted">
              <div className="flex items-center gap-2">
                <span className="font-mono text-[11px] uppercase tracking-wider text-blue-dark font-semibold">
                  Parsed Procurement Intent
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded border border-blue-border bg-blue-soft text-blue-dark font-medium">
                  {plan.ai_provider === 'gemini' ? `Gemini (${plan.model_name || 'Flash'})` : 'Mock Engine'}
                </span>
                {plan.fallback_used && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded border border-accent-amber-border bg-accent-amber-bg text-accent-amber font-medium flex items-center gap-1">
                    <AlertCircle className="w-2.5 h-2.5" />
                    Resilient Fallback Model
                  </span>
                )}
              </div>
              <span className="font-mono text-[10px] text-slate-muted">
                Plan ID: {plan.plan_id.slice(0, 8)}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-navy leading-relaxed italic">
              "{plan.intent_interpretation}"
            </p>

            {plan.clarification_needed && (
              <div className="mt-3 p-3 rounded bg-accent-amber-bg border border-accent-amber-border flex items-start gap-2 text-xs text-accent-amber">
                <HelpCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold block">Clarification Prompt</span>
                  <p className="mt-0.5 leading-relaxed">{plan.clarification_needed}</p>
                </div>
              </div>
            )}
          </div>

          {/* Warnings List */}
          {plan.warnings.length > 0 && (
            <div className="rounded p-3.5 bg-accent-amber-bg border border-accent-amber-border text-xs space-y-1.5">
              <div className="flex items-center gap-1.5 font-semibold text-accent-amber">
                <Info className="w-3.5 h-3.5" />
                <span>Catalog Grounding & Budget Adjustments</span>
              </div>
              <ul className="list-disc list-inside text-navy-soft text-[11px] space-y-0.5 pl-1">
                {plan.warnings.map((w, idx) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Grounded Item Recommendations */}
          {plan.recommendations.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-baseline justify-between text-xs text-slate-muted">
                <span className="font-mono text-[11px] uppercase tracking-wider text-navy font-semibold">
                  Grounded Proposals ({plan.recommendations.length} Items)
                </span>
                <span className="font-mono text-[10px]">Authoritative Merchant Pricing</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {plan.recommendations.map((rec: GroundedRecommendation) => (
                  <div
                    key={rec.sku}
                    className="p-4 rounded border border-slate-border bg-white hover:border-blue-primary/40 transition-colors flex flex-col justify-between gap-3"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="text-xs font-semibold text-navy">{rec.name}</h4>
                        <span className="text-[10px] font-mono text-slate-muted px-1.5 py-0.5 rounded bg-surface-subtle border border-slate-border shrink-0">
                          {rec.sku}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-muted mt-2 leading-relaxed">
                        {rec.reason}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-slate-line flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-muted text-[11px]">
                          Qty: <strong className="text-navy">{rec.recommended_quantity}</strong>
                        </span>
                        <span className="text-slate-border">•</span>
                        <span className="text-accent-forest font-mono text-[11px] font-medium">
                          {rec.stock_available} in stock
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="font-mono font-semibold text-navy tabular-nums">
                          ${rec.total_price}
                        </span>
                        <span className="text-[10px] font-mono text-slate-muted ml-1">
                          USD
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Financials & Risk Scoring Card */}
          <div className="p-4 rounded border border-slate-border bg-surface-subtle grid grid-cols-1 sm:grid-cols-2 gap-4 items-center">
            {/* Left: Totals & Budget */}
            <div className="space-y-1">
              <div className="flex items-baseline gap-2">
                <span className="text-xs text-slate-muted">Proposal Subtotal:</span>
                <span className="font-serif text-xl text-navy font-normal tabular-nums">
                  ${plan.subtotal}
                </span>
                <span className="text-xs font-mono text-slate-muted">USD</span>
              </div>

              {plan.budget && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-muted">Target Budget: ${plan.budget}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-medium ${
                      plan.budget_status === 'WITHIN_BUDGET'
                        ? 'bg-blue-soft text-blue-dark border border-blue-border'
                        : 'bg-accent-amber-bg text-accent-amber border border-accent-amber-border'
                    }`}
                  >
                    {plan.budget_status === 'WITHIN_BUDGET'
                      ? `Within budget ($${plan.budget_difference} surplus)`
                      : `Exceeds budget by $${plan.budget_difference}`}
                  </span>
                </div>
              )}
            </div>

            {/* Right: Explainable Transaction Risk Assessment */}
            <div className="p-3 rounded bg-white border border-slate-border space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-xs font-medium text-navy">Explainable Risk</span>
                {getRiskBadge(plan.risk_assessment.risk_level, plan.risk_assessment.score)}
              </div>
              <p className="text-[11px] text-slate-muted leading-relaxed">
                {plan.risk_assessment.reasons[0] || 'Parameters verified against warehouse catalog.'}
              </p>
            </div>
          </div>

          {/* Action Row & Explicit Disclosure */}
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-[11px] text-slate-muted text-center sm:text-left leading-relaxed">
              Advisory only. Recommendations are grounded in warehouse inventory and require buyer confirmation.
            </p>

            {plan.is_actionable && (
              <button
                type="button"
                onClick={handleApplyToCart}
                disabled={addedSuccess}
                className={`px-5 py-2.5 rounded text-xs font-medium flex items-center justify-center gap-1.5 transition-colors shrink-0 shadow-xs ${
                  addedSuccess
                    ? 'bg-accent-forest text-white'
                    : 'bg-blue-primary hover:bg-blue-hover text-white'
                }`}
              >
                {addedSuccess ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-white" />
                    <span>Added to Order • Opening Review...</span>
                  </>
                ) : (
                  <>
                    <Plus className="w-3.5 h-3.5" />
                    <span>Apply Proposal to Order</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  );
};
