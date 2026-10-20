import React from 'react';
import type { HealthStatus } from '../types/catalog';
import { ShieldCheck, Server, AlertCircle, ShoppingBag } from 'lucide-react';

interface NavbarProps {
  health: HealthStatus | null;
  error: string | null;
  cartCount: number;
  cartTotal: string;
  onOpenCart: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  error,
  cartCount,
  cartTotal,
  onOpenCart,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <span className="font-bold text-white text-xl tracking-wider">P</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">PayPilot AI</span>
              <span className="text-[10px] font-semibold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full">
                M2: PayPal Sandbox Live
              </span>
            </div>
            <p className="text-xs text-slate-400">Autonomous Payment Operations & Purchasing Agent</p>
          </div>
        </div>

        <div className="flex items-center gap-3 sm:gap-4">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-300">PayPal Sandbox Environment</span>
          </div>

          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
            <Server className="w-3.5 h-3.5 text-slate-400" />
            {health ? (
              <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Backend Online (v{health.version})
              </span>
            ) : error ? (
              <span className="flex items-center gap-1.5 text-rose-400 font-medium">
                <AlertCircle className="w-3.5 h-3.5" />
                Backend Disconnected
              </span>
            ) : (
              <span className="text-slate-400">Connecting...</span>
            )}
          </div>

          {/* Cart / Purchase Order Button */}
          <button
            onClick={onOpenCart}
            className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-all shadow-md shadow-indigo-600/20"
          >
            <div className="relative">
              <ShoppingBag className="w-4 h-4" />
              {cartCount > 0 && (
                <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-emerald-500 text-[10px] font-bold text-slate-950 flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </div>
            <span>Purchase Order {cartCount > 0 ? `($${cartTotal})` : ''}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
