import React, { useState } from 'react';
import type { CaptureResult } from '../types/order';
import { AlertCircle, Check, Download, Loader2, ShieldCheck, X } from 'lucide-react';
import { triggerReceiptDownload } from '../services/api';

interface ReceiptModalProps {
  result: CaptureResult | null;
  onClose: () => void;
}

export const ReceiptModal: React.FC<ReceiptModalProps> = ({ result, onClose }) => {
  const [downloading, setDownloading] = useState<boolean>(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  React.useEffect(() => {
    if (!result) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [result, onClose]);

  const handleDownloadPdf = async () => {
    if (!result?.order_id) return;
    setDownloading(true);
    setDownloadError(null);
    try {
      await triggerReceiptDownload(result.order_id);
    } catch (err) {
      setDownloadError(err instanceof Error ? err.message : 'Failed to download receipt PDF.');
    } finally {
      setDownloading(false);
    }
  };

  if (!result) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy/40 backdrop-blur-xs"
      role="dialog"
      aria-modal="true"
      aria-labelledby="receipt-title"
    >
      <div className="relative w-full max-w-lg rounded border border-slate-border bg-white p-6 sm:p-8 shadow-xl space-y-6">
        <button
          onClick={onClose}
          type="button"
          aria-label="Close receipt modal"
          className="absolute top-5 right-5 p-2 rounded text-slate-muted hover:text-navy hover:bg-slate-border/30 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="flex items-start gap-3.5 pb-4 border-b border-slate-line">
          <div className="w-10 h-10 rounded border border-accent-forest-border bg-accent-forest-bg flex items-center justify-center text-accent-forest shrink-0">
            <Check className="w-5 h-5 stroke-[2]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-accent-forest font-semibold">
                Settlement Completed
              </span>
              <span className="text-slate-border">•</span>
              <span className="text-[10px] font-mono text-slate-muted">
                PayPal Orders v2
              </span>
            </div>
            <h2 id="receipt-title" className="font-serif text-2xl text-navy font-normal tracking-tight mt-0.5">
              Settlement Receipt
            </h2>
          </div>
        </div>

        {/* Amount & Identifiers */}
        <div className="p-4 rounded border border-slate-border bg-surface-subtle space-y-4">
          <div className="flex items-baseline justify-between border-b border-slate-border pb-3">
            <span className="text-xs uppercase font-mono tracking-wider text-slate-muted font-medium">
              Captured Total
            </span>
            <div className="text-right">
              <span className="font-serif text-2xl font-normal text-navy tabular-nums">
                ${result.captured_amount}
              </span>
              <span className="text-xs font-mono text-slate-muted ml-1.5">
                {result.currency}
              </span>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-muted">PayPal Capture ID</span>
              <span className="font-mono text-navy text-[11px] font-medium">
                {result.paypal_capture_id}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-muted">PayPal Order ID</span>
              <span className="font-mono text-navy-soft text-[11px]">
                {result.paypal_order_id}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-muted">Internal Order ID</span>
              <span className="font-mono text-slate-muted text-[10px]">
                {result.order_id}
              </span>
            </div>

            {result.captured_at && (
              <div className="flex items-center justify-between">
                <span className="text-slate-muted">Captured At</span>
                <span className="text-navy-soft font-mono text-[11px]">
                  {new Date(result.captured_at).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Verification Note */}
        <div className="p-3 rounded border border-slate-border bg-canvas text-xs text-navy-soft flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-accent-forest shrink-0 mt-0.5" />
          <span className="text-[11px] leading-relaxed">
            Verified server-side through PayPal Orders v2 REST API. Authoritative prices, inventory deductions, and audit events were permanently recorded.
          </span>
        </div>

        {/* Download Error Banner */}
        {downloadError && (
          <div className="p-3 rounded bg-accent-crimson-bg border border-accent-crimson-border flex items-center gap-2 text-xs text-accent-crimson">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{downloadError}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-2 pt-2">
          <button
            onClick={handleDownloadPdf}
            disabled={downloading}
            type="button"
            className="w-full py-2.5 rounded bg-blue-primary hover:bg-blue-hover disabled:opacity-50 text-white text-xs font-medium tracking-wide flex items-center justify-center gap-2 transition-colors shadow-xs"
          >
            {downloading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Generating Official PDF...</span>
              </>
            ) : (
              <>
                <Download className="w-3.5 h-3.5" />
                <span>Download Official Receipt (PDF)</span>
              </>
            )}
          </button>

          <button
            onClick={onClose}
            type="button"
            className="w-full py-2 rounded bg-white hover:bg-slate-border/20 text-slate-muted hover:text-navy text-xs font-medium border border-slate-border transition-colors"
          >
            Return to Catalog
          </button>
        </div>
      </div>
    </div>
  );
};
