import React, { useState } from 'react';
import type { Order } from '../types/order';
import {
  X,
  ChevronDown,
  ChevronUp,
  Clock,
  RefreshCw,
  Receipt,
  ShieldCheck,
  Download,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { triggerReceiptDownload } from '../services/api';

interface TransactionHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  orders: Order[];
  onRefresh: () => void;
  loading: boolean;
}

export const TransactionHistoryModal: React.FC<TransactionHistoryModalProps> = ({
  isOpen,
  onClose,
  orders,
  onRefresh,
  loading,
}) => {
  const [expandedOrderId, setExpandedOrderId] = useState<string | null>(null);
  const [downloadingOrderId, setDownloadingOrderId] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleDownload = async (orderId: string) => {
    setDownloadingOrderId(orderId);
    setDownloadError(null);
    try {
      await triggerReceiptDownload(orderId);
    } catch (err) {
      setDownloadError(err instanceof Error ? err.message : 'Failed to download receipt');
    } finally {
      setDownloadingOrderId(null);
    }
  };

  React.useEffect(() => {
    if (!isOpen) return;
    const params = new URLSearchParams(window.location.search);
    const targetOrder = params.get('order');
    if (targetOrder) {
      setExpandedOrderId(targetOrder);
    } else if (orders.length > 0 && !expandedOrderId) {
      const completed = orders.find((o) => o.status === 'COMPLETED');
      if (completed) setExpandedOrderId(completed.id);
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const toggleExpand = (orderId: string) => {
    setExpandedOrderId(expandedOrderId === orderId ? null : orderId);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-accent-forest-bg text-accent-forest border border-accent-forest-border">
            <ShieldCheck className="w-3 h-3" />
            COMPLETED
          </span>
        );
      case 'CANCELLED':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-accent-amber-bg text-accent-amber border border-accent-amber-border">
            CANCELLED
          </span>
        );
      case 'FAILED':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-accent-crimson-bg text-accent-crimson border border-accent-crimson-border">
            FAILED
          </span>
        );
      case 'CAPTURING':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-blue-soft text-blue-dark border border-blue-border animate-pulse">
            CAPTURING
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-surface-subtle text-slate-muted border border-slate-border">
            {status}
          </span>
        );
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy/40 backdrop-blur-xs"
      role="dialog"
      aria-modal="true"
      aria-labelledby="history-title"
    >
      <div className="relative w-full max-w-3xl max-h-[85vh] rounded border border-slate-border bg-white flex flex-col shadow-xl overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-slate-border bg-canvas flex items-center justify-between">
          <div>
            <div className="flex items-baseline gap-2">
              <h2 id="history-title" className="font-serif text-xl sm:text-2xl text-navy font-normal tracking-tight">
                Transaction Ledger
              </h2>
              <span className="text-[10px] font-mono uppercase tracking-widest text-slate-muted">
                Audit Trail
              </span>
            </div>
            <p className="text-xs text-slate-muted mt-0.5">
              Authoritative database records &amp; verified PayPal settlements
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onRefresh}
              disabled={loading}
              type="button"
              aria-label="Refresh transaction ledger"
              className="p-2 rounded text-slate-muted hover:text-blue-primary hover:bg-blue-soft/50 transition-colors disabled:opacity-40"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              type="button"
              aria-label="Close transaction ledger"
              className="p-2 rounded text-slate-muted hover:text-navy hover:bg-slate-border/40 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3 bg-white">
          {orders.length === 0 ? (
            <div className="py-20 text-center space-y-3">
              <div className="w-12 h-12 rounded border border-blue-border bg-blue-soft flex items-center justify-center mx-auto text-blue-primary">
                <Receipt className="w-5 h-5 stroke-[1.5]" />
              </div>
              <h3 className="font-serif text-lg text-navy font-normal">No recorded transactions</h3>
              <p className="text-xs text-slate-muted max-w-xs mx-auto leading-relaxed">
                Initiated and settled purchase orders will be permanently archived and auditable here.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {orders.map((order) => {
                const isExpanded = expandedOrderId === order.id;
                return (
                  <div
                    key={order.id}
                    className="rounded border border-slate-border bg-canvas/40 overflow-hidden transition-colors"
                  >
                    <div
                      role="button"
                      tabIndex={0}
                      aria-expanded={isExpanded}
                      aria-label={`Toggle details for order ${order.id}`}
                      onClick={() => toggleExpand(order.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          toggleExpand(order.id);
                        }
                      }}
                      className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer hover:bg-blue-soft/20 focus:outline-none focus:ring-1 focus:ring-blue-primary/50 transition-colors"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2.5">
                          {getStatusBadge(order.status)}
                          <span className="font-mono text-xs text-navy font-semibold">
                            Order {order.id.slice(0, 8)}...
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-[11px] text-slate-muted">
                          <Clock className="w-3 h-3 text-slate-muted" />
                          <span>{new Date(order.created_at).toLocaleString()}</span>
                          <span className="text-slate-border">•</span>
                          <span>{order.items.length} item(s)</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between sm:justify-end gap-4 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-line">
                        <div className="text-left sm:text-right">
                          <span className="font-serif text-lg font-normal text-navy tabular-nums">
                            ${order.total_amount}
                          </span>
                          <span className="text-xs font-mono text-slate-muted ml-1">
                            {order.currency}
                          </span>
                        </div>
                        <div className="text-slate-muted">
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-blue-primary" />
                          ) : (
                            <ChevronDown className="w-4 h-4" />
                          )}
                        </div>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="p-4 border-t border-slate-border bg-white space-y-4">
                        {/* PayPal identifiers */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                          <div className="p-2.5 rounded bg-surface-subtle border border-slate-border">
                            <span className="text-slate-muted block text-[10px] uppercase font-mono tracking-wider font-semibold">
                              PayPal Order ID
                            </span>
                            <span className="font-mono text-navy text-[11px] font-medium mt-0.5 block">
                              {order.paypal_order_id || 'Not Assigned'}
                            </span>
                          </div>

                          <div className="p-2.5 rounded bg-surface-subtle border border-slate-border">
                            <span className="text-slate-muted block text-[10px] uppercase font-mono tracking-wider font-semibold">
                              PayPal Capture ID
                            </span>
                            <span className="font-mono text-blue-dark text-[11px] font-medium mt-0.5 block">
                              {order.paypal_capture_id || 'None'}
                            </span>
                          </div>
                        </div>

                        {/* Snapshot Items Breakdown */}
                        <div>
                          <span className="text-[10px] uppercase font-mono tracking-wider font-semibold text-slate-muted block mb-2">
                            Snapshot Items &amp; Authoritative Prices
                          </span>
                          <div className="space-y-1.5">
                            {order.items.map((it) => (
                              <div
                                key={it.id}
                                className="flex items-center justify-between text-xs py-2 px-3 rounded bg-surface-subtle border border-slate-border"
                              >
                                <div>
                                  <span className="text-navy font-medium">{it.name}</span>
                                  <span className="text-slate-muted font-mono text-[11px] ml-2">
                                    ({it.quantity} × ${it.unit_price})
                                  </span>
                                </div>
                                <span className="font-mono font-semibold text-navy tabular-nums">
                                  ${it.total_price}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Audit Trail */}
                        {order.audit_logs && order.audit_logs.length > 0 && (
                          <div>
                            <span className="text-[10px] uppercase font-mono tracking-wider font-semibold text-slate-muted block mb-2">
                              Audit Event Timeline
                            </span>
                            <div className="space-y-1 text-xs">
                              {order.audit_logs.map((log) => (
                                <div
                                  key={log.id}
                                  className="flex items-center justify-between py-1.5 px-3 rounded bg-canvas text-[11px] border border-slate-border"
                                >
                                  <div className="flex items-center gap-2">
                                    <span className="font-mono text-blue-primary font-semibold">
                                      {log.event_type}
                                    </span>
                                    <span className="text-slate-muted text-[10px]">
                                      via {log.actor}
                                    </span>
                                  </div>
                                  <span className="text-slate-muted font-mono text-[10px]">
                                    {new Date(log.created_at).toLocaleTimeString()}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Download Official Receipt for Completed Orders */}
                        {order.status === 'COMPLETED' && (
                          <div className="pt-2 border-t border-slate-line flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <div className="flex items-center gap-2 text-xs text-accent-forest">
                              <ShieldCheck className="w-4 h-4 shrink-0" />
                              <span className="font-mono text-[11px] font-medium">Authoritative Settled Transaction</span>
                            </div>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDownload(order.id);
                              }}
                              disabled={downloadingOrderId === order.id}
                              className="inline-flex items-center justify-center gap-1.5 px-3.5 py-1.5 rounded text-xs font-medium bg-blue-primary hover:bg-blue-hover text-white transition-colors disabled:opacity-50 shadow-xs"
                            >
                              {downloadingOrderId === order.id ? (
                                <>
                                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                  <span>Downloading...</span>
                                </>
                              ) : (
                                <>
                                  <Download className="w-3.5 h-3.5" />
                                  <span>Download Official Receipt (PDF)</span>
                                </>
                              )}
                            </button>
                          </div>
                        )}

                        {downloadError && downloadingOrderId === null && expandedOrderId === order.id && (
                          <div className="p-2.5 rounded bg-accent-crimson-bg border border-accent-crimson-border flex items-center gap-2 text-xs text-accent-crimson">
                            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                            <span>{downloadError}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
