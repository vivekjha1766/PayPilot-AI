import React, { useState } from 'react';
import type { Order } from '../types/order';
import {
  History,
  X,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Clock,
  RefreshCw,
  Receipt,
} from 'lucide-react';

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

  if (!isOpen) return null;

  const toggleExpand = (orderId: string) => {
    setExpandedOrderId(expandedOrderId === orderId ? null : orderId);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <ShieldCheck className="w-3.5 h-3.5" />
            COMPLETED
          </span>
        );
      case 'CANCELLED':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            CANCELLED
          </span>
        );
      case 'FAILED':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
            FAILED
          </span>
        );
      case 'CAPTURING':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 animate-pulse">
            CAPTURING
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl max-h-[85vh] rounded-3xl border border-slate-800 bg-slate-900 flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">Persisted Transaction History</h2>
              <p className="text-xs text-slate-400">Database Records & Verified PayPal Captures</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onRefresh}
              disabled={loading}
              title="Refresh Transactions"
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {orders.length === 0 ? (
            <div className="py-16 text-center space-y-3">
              <Receipt className="w-12 h-12 text-slate-700 mx-auto" />
              <h3 className="text-sm font-semibold text-slate-300">No transactions recorded yet</h3>
              <p className="text-xs text-slate-500 max-w-xs mx-auto">
                Completed and initiated orders will be permanently stored and auditable here.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {orders.map((order) => {
                const isExpanded = expandedOrderId === order.id;
                return (
                  <div
                    key={order.id}
                    className="rounded-2xl border border-slate-800 bg-slate-950/60 overflow-hidden transition-all"
                  >
                    <div
                      onClick={() => toggleExpand(order.id)}
                      className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-900/60 transition-colors"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2.5">
                          {getStatusBadge(order.status)}
                          <span className="font-mono text-xs text-slate-300 font-semibold">
                            Order {order.id.slice(0, 8)}...
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-[11px] text-slate-500">
                          <Clock className="w-3.5 h-3.5" />
                          <span>{new Date(order.created_at).toLocaleString()}</span>
                          <span>•</span>
                          <span>{order.items.length} item(s)</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <span className="text-base font-bold text-white">
                            ${order.total_amount}
                          </span>
                          <span className="text-xs text-slate-400 ml-1">
                            {order.currency}
                          </span>
                        </div>
                        <div className="text-slate-500">
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4" />
                          ) : (
                            <ChevronDown className="w-4 h-4" />
                          )}
                        </div>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="p-4 border-t border-slate-800/80 bg-slate-900/40 space-y-4">
                        {/* PayPal identifiers */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                          <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                            <span className="text-slate-500 block text-[10px] uppercase font-semibold">
                              PayPal Order ID
                            </span>
                            <span className="font-mono text-slate-300 font-medium text-[11px]">
                              {order.paypal_order_id || 'Not Assigned'}
                            </span>
                          </div>

                          <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                            <span className="text-slate-500 block text-[10px] uppercase font-semibold">
                              PayPal Capture ID
                            </span>
                            <span className="font-mono text-emerald-400 font-semibold text-[11px]">
                              {order.paypal_capture_id || 'None'}
                            </span>
                          </div>
                        </div>

                        {/* Items Breakdown */}
                        <div>
                          <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-2">
                            Snapshot Items & Authoritative Prices
                          </span>
                          <div className="space-y-1.5">
                            {order.items.map((it) => (
                              <div
                                key={it.id}
                                className="flex items-center justify-between text-xs py-1.5 px-3 rounded-lg bg-slate-950/80 border border-slate-800"
                              >
                                <div>
                                  <span className="text-slate-200 font-medium">{it.name}</span>
                                  <span className="text-slate-500 text-[11px] ml-2">
                                    ({it.quantity} × ${it.unit_price})
                                  </span>
                                </div>
                                <span className="font-bold text-white">${it.total_price}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Audit Trail */}
                        {order.audit_logs && order.audit_logs.length > 0 && (
                          <div>
                            <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-2">
                              Audit Event Timeline
                            </span>
                            <div className="space-y-1 text-xs">
                              {order.audit_logs.map((log) => (
                                <div
                                  key={log.id}
                                  className="flex items-center justify-between py-1 px-2.5 rounded bg-slate-950/50 text-[11px] border border-slate-800/50"
                                >
                                  <div className="flex items-center gap-2">
                                    <span className="font-mono text-indigo-400 font-semibold">
                                      {log.event_type}
                                    </span>
                                    <span className="text-slate-500 text-[10px]">
                                      via {log.actor}
                                    </span>
                                  </div>
                                  <span className="text-slate-500 text-[10px]">
                                    {new Date(log.created_at).toLocaleTimeString()}
                                  </span>
                                </div>
                              ))}
                            </div>
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
