import React from 'react';
import type { CartItem, CaptureResult, PaymentConfig } from '../types/order';
import { PayPalButtonWrapper } from './PayPalButtonWrapper';
import { ShoppingBag, X, Plus, Minus, Trash2, AlertCircle } from 'lucide-react';

interface CheckoutDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  cartItems: CartItem[];
  onUpdateQuantity: (sku: string, delta: number) => void;
  onRemoveItem: (sku: string) => void;
  onClearCart: () => void;
  paymentConfig: PaymentConfig | null;
  onCheckoutSuccess: (result: CaptureResult) => void;
  onCheckoutCancel: () => void;
  checkoutError: string | null;
  setCheckoutError: (err: string | null) => void;
}

export const CheckoutDrawer: React.FC<CheckoutDrawerProps> = ({
  isOpen,
  onClose,
  cartItems,
  onUpdateQuantity,
  onRemoveItem,
  onClearCart,
  paymentConfig,
  onCheckoutSuccess,
  onCheckoutCancel,
  checkoutError,
  setCheckoutError,
}) => {
  if (!isOpen) return null;

  const totalAmount = cartItems.reduce(
    (sum, item) => sum + parseFloat(item.unit_price) * item.quantity,
    0
  );
  const currency = paymentConfig?.currency || 'USD';

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div
        className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-6 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <ShoppingBag className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">Purchase Order Review</h2>
                <p className="text-xs text-slate-400">Authoritative Server-Validated Items</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Cart Items List */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {checkoutError && (
              <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                <div className="flex-1 text-xs">
                  <span className="font-semibold text-rose-300 block">Checkout Error</span>
                  <p className="text-rose-400/90 mt-0.5">{checkoutError}</p>
                </div>
                <button
                  onClick={() => setCheckoutError(null)}
                  className="text-rose-400 hover:text-rose-200"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            {cartItems.length === 0 ? (
              <div className="py-16 text-center space-y-3">
                <ShoppingBag className="w-12 h-12 text-slate-700 mx-auto" />
                <h3 className="text-sm font-semibold text-slate-300">Your purchase order is empty</h3>
                <p className="text-xs text-slate-500 max-w-xs mx-auto">
                  Add items from the office equipment catalog to initiate a verified PayPal sandbox purchase.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {cartItems.map((item) => (
                  <div
                    key={item.sku}
                    className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 flex items-start justify-between gap-3"
                  >
                    <div className="flex-1 min-w-0">
                      <h4 className="text-xs font-semibold text-white truncate">{item.name}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[10px] font-mono text-slate-400">SKU: {item.sku}</span>
                        <span className="text-[10px] text-slate-500">•</span>
                        <span className="text-xs font-semibold text-indigo-400">${item.unit_price}</span>
                      </div>

                      {/* Quantity Controls */}
                      <div className="flex items-center gap-2 mt-3">
                        <button
                          onClick={() => onUpdateQuantity(item.sku, -1)}
                          disabled={item.quantity <= 1}
                          className="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 flex items-center justify-center text-slate-300 transition-colors"
                        >
                          <Minus className="w-3.5 h-3.5" />
                        </button>
                        <span className="text-xs font-semibold text-white w-6 text-center">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => onUpdateQuantity(item.sku, 1)}
                          disabled={item.quantity >= item.stock}
                          className="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 flex items-center justify-center text-slate-300 transition-colors"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    <div className="text-right flex flex-col justify-between items-end h-full">
                      <button
                        onClick={() => onRemoveItem(item.sku)}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-900 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <span className="text-xs font-bold text-white mt-4">
                        ${(parseFloat(item.unit_price) * item.quantity).toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer & Checkout Area */}
          {cartItems.length > 0 && (
            <div className="p-6 border-t border-slate-800 bg-slate-950/80 space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Authoritative Subtotal</span>
                  <span className="font-medium text-slate-300">
                    ${totalAmount.toFixed(2)} {currency}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Estimated Tax & Sandbox Fee</span>
                  <span className="font-medium text-slate-300">$0.00 {currency}</span>
                </div>
                <div className="pt-2 border-t border-slate-800/80 flex items-baseline justify-between">
                  <span className="text-sm font-bold text-white">Order Total</span>
                  <div className="text-right">
                    <span className="text-xl font-extrabold text-white">
                      ${totalAmount.toFixed(2)}
                    </span>
                    <span className="text-xs font-semibold text-slate-400 ml-1.5">
                      {currency}
                    </span>
                  </div>
                </div>
              </div>

              {/* Real PayPal Sandbox Button Wrapper */}
              {paymentConfig && (
                <PayPalButtonWrapper
                  config={paymentConfig}
                  cartItems={cartItems}
                  onSuccess={(result) => {
                    onClearCart();
                    onClose();
                    onCheckoutSuccess(result);
                  }}
                  onCancel={() => {
                    setCheckoutError('Checkout was cancelled by buyer.');
                    onCheckoutCancel();
                  }}
                  onError={(err) => setCheckoutError(err)}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
