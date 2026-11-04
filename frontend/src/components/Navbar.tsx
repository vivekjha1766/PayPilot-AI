import React from 'react';
import type { HealthStatus } from '../types/catalog';
import { ShoppingBag, History, AlertCircle } from 'lucide-react';

interface NavbarProps {
  health: HealthStatus | null;
  error: string | null;
  cartCount: number;
  cartTotal: string;
  onOpenCart: () => void;
  onOpenHistory: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  error,
  cartCount,
  cartTotal,
  onOpenCart,
  onOpenHistory,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-slate-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Typographic Wordmark & Blue Brand Accent */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded border border-blue-border bg-blue-soft flex items-center justify-center text-blue-primary shadow-xs">
            <span className="font-serif italic font-bold text-lg leading-none">P</span>
          </div>
          <div className="flex items-baseline gap-2.5">
            <span className="font-serif text-xl sm:text-2xl text-navy tracking-tight font-normal">
              PayPilot
            </span>
            <span className="hidden sm:inline-block text-[10px] uppercase font-mono tracking-widest text-slate-muted border-l border-slate-border pl-2.5">
              Fintech Operations
            </span>
          </div>
        </div>

        {/* Status Indicators & Navigation Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Environment Indicator */}
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded border border-slate-border bg-white text-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-primary" />
            <span className="font-mono text-[11px] text-slate-muted">ENV:</span>
            <span className="font-medium text-navy text-[11px]">PayPal Sandbox</span>
          </div>

          {/* Backend Health Status */}
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded border border-slate-border bg-white text-xs">
            {health ? (
              <span className="flex items-center gap-1.5 text-slate-muted text-[11px] font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-accent-forest inline-block" />
                <span className="text-navy font-sans text-xs font-medium">API Online</span>
                <span className="text-[10px] text-slate-muted">v{health.version}</span>
              </span>
            ) : error ? (
              <span className="flex items-center gap-1.5 text-accent-crimson text-xs font-medium">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Disconnected</span>
              </span>
            ) : (
              <span className="text-slate-muted text-xs">Connecting...</span>
            )}
          </div>

          {/* Transaction History Button */}
          <button
            onClick={onOpenHistory}
            type="button"
            aria-label="View transaction history"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded border border-slate-border bg-white hover:bg-blue-soft/60 hover:border-blue-border hover:text-blue-primary text-navy text-xs font-medium transition-colors"
          >
            <History className="w-3.5 h-3.5 text-slate-muted" />
            <span className="hidden sm:inline">History</span>
          </button>

          {/* Cart / Order Trigger in Primary Brand Blue */}
          <button
            onClick={onOpenCart}
            type="button"
            aria-label={`Open purchase order, ${cartCount} items totaling $${cartTotal}`}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded bg-blue-primary hover:bg-blue-hover text-white text-xs font-medium transition-colors shadow-xs"
          >
            <ShoppingBag className="w-3.5 h-3.5" />
            <span>Order</span>
            {cartCount > 0 ? (
              <span className="inline-flex items-center gap-1 pl-1 border-l border-blue-hover">
                <span className="w-4 h-4 rounded-full bg-white text-blue-primary text-[10px] font-bold flex items-center justify-center">
                  {cartCount}
                </span>
                <span className="hidden sm:inline tabular-nums font-mono text-[11px]">
                  ${cartTotal}
                </span>
              </span>
            ) : null}
          </button>
        </div>
      </div>
    </header>
  );
};
