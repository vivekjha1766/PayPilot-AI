import React from 'react';
import type { CaptureResult } from '../types/order';
import { CheckCircle2, ShieldCheck, X } from 'lucide-react';

interface ReceiptModalProps {
  result: CaptureResult | null;
  onClose: () => void;
}

export const ReceiptModal: React.FC<ReceiptModalProps> = ({ result, onClose }) => {
  if (!result) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg rounded-3xl border border-emerald-500/30 bg-slate-900 p-8 shadow-2xl shadow-emerald-500/10 space-y-6">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <div>
            <div className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">
              <ShieldCheck className="w-3.5 h-3.5" />
              Verified PayPal Capture
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Payment Completed</h2>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-3">
          <div className="flex items-baseline justify-between border-b border-slate-800/80 pb-3">
            <span className="text-xs text-slate-400 font-medium">Captured Total</span>
            <div className="text-right">
              <span className="text-2xl font-extrabold text-white">
                ${result.captured_amount}
              </span>
              <span className="text-xs font-semibold text-slate-400 ml-1.5">
                {result.currency}
              </span>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">PayPal Capture ID</span>
              <span className="font-mono font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                {result.paypal_capture_id}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400">PayPal Order ID</span>
              <span className="font-mono text-slate-300">
                {result.paypal_order_id}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400">Internal Order ID</span>
              <span className="font-mono text-slate-400 text-[11px]">
                {result.order_id}
              </span>
            </div>

            {result.captured_at && (
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Captured At</span>
                <span className="text-slate-300">
                  {new Date(result.captured_at).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-800/50 border border-slate-700/60 text-xs text-slate-300 flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <span>
            Payment verified server-side using the PayPal Orders v2 REST API. Authoritative prices, inventory deductions, and audit events were permanently recorded.
          </span>
        </div>

        <button
          onClick={onClose}
          className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold tracking-wide transition-all shadow-lg shadow-indigo-600/20"
        >
          Return to Catalog
        </button>
      </div>
    </div>
  );
};
