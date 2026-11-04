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
  React.useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const totalAmount = cartItems.reduce(
    (sum, item) => sum + parseFloat(item.unit_price) * item.quantity,
    0
  );
  const currency = paymentConfig?.currency || 'USD';

  return (
    <div className="fixed inset-0 z-50 overflow-hidden" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-navy/40 backdrop-blur-xs transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white border-l border-slate-border shadow-xl flex flex-col">
          {/* Header */}
          <div className="p-6 border-b border-slate-border bg-canvas flex items-center justify-between">
            <div>
              <div className="flex items-baseline gap-2">
                <h2 id="drawer-title" className="font-serif text-xl text-navy font-normal tracking-tight">
                  Purchase Order
                </h2>
                <span className="text-[10px] font-mono uppercase tracking-widest text-slate-muted">
                  Review
                </span>
              </div>
              <p className="text-xs text-slate-muted mt-0.5">
                Authoritative server-validated item pricing
              </p>
            </div>
            <button
              onClick={onClose}
              type="button"
              aria-label="Close purchase order drawer"
              className="p-2 rounded text-slate-muted hover:text-navy hover:bg-slate-border/40 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Cart Items List */}
          <div className="flex-1 overflow-y-auto p-6 space-y-3 bg-white">
            {checkoutError && (
              <div className="rounded p-4 bg-accent-crimson-bg border border-accent-crimson-border flex items-start gap-3 text-xs text-accent-crimson">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-accent-crimson" />
                <div className="flex-1">
                  <span className="font-semibold block">Checkout Notice</span>
                  <p className="mt-0.5 leading-relaxed">{checkoutError}</p>
                </div>
                <button
                  onClick={() => setCheckoutError(null)}
                  type="button"
                  aria-label="Dismiss error"
                  className="text-accent-crimson hover:text-navy"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {cartItems.length === 0 ? (
              <div className="py-20 text-center space-y-3">
                <div className="w-12 h-12 rounded border border-blue-border bg-blue-soft flex items-center justify-center mx-auto text-blue-primary">
                  <ShoppingBag className="w-5 h-5 stroke-[1.5]" />
                </div>
                <h3 className="font-serif text-lg text-navy font-normal">Your order is empty</h3>
                <p className="text-xs text-slate-muted max-w-xs mx-auto leading-relaxed">
                  Add items from the merchant catalog or request a grounded plan from the purchasing assistant.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {cartItems.map((item) => (
                  <div
                    key={item.sku}
                    className="p-4 rounded border border-slate-border bg-canvas/60 flex items-start justify-between gap-3"
                  >
                    <div className="flex-1 min-w-0">
                      <h4 className="text-xs font-semibold text-navy truncate">{item.name}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[10px] font-mono text-slate-muted">
                          {item.sku}
                        </span>
                        <span className="text-slate-border">•</span>
                        <span className="text-xs font-mono text-navy font-medium">
                          ${item.unit_price} {item.currency}
                        </span>
                      </div>

                      {/* Quantity Controls */}
                      <div className="flex items-center gap-2 mt-3">
                        <button
                          onClick={() => onUpdateQuantity(item.sku, -1)}
                          disabled={item.quantity <= 1}
                          type="button"
                          aria-label={`Decrease quantity for ${item.name}`}
                          className="w-6 h-6 rounded border border-slate-border bg-white hover:border-blue-border hover:text-blue-primary hover:bg-blue-soft/50 disabled:opacity-30 flex items-center justify-center text-navy transition-colors"
                        >
                          <Minus className="w-3 h-3" />
                        </button>
                        <span className="text-xs font-mono font-semibold text-navy w-6 text-center tabular-nums">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => onUpdateQuantity(item.sku, 1)}
                          disabled={item.quantity >= item.stock}
                          type="button"
                          aria-label={`Increase quantity for ${item.name}`}
                          className="w-6 h-6 rounded border border-slate-border bg-white hover:border-blue-border hover:text-blue-primary hover:bg-blue-soft/50 disabled:opacity-30 flex items-center justify-center text-navy transition-colors"
                        >
                          <Plus className="w-3 h-3" />
                        </button>
                        {item.quantity >= item.stock && (
                          <span className="text-[10px] text-accent-amber font-mono ml-1">
                            Max stock
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="text-right flex flex-col justify-between items-end h-full">
                      <button
                        onClick={() => onRemoveItem(item.sku)}
                        type="button"
                        aria-label={`Remove ${item.name} from cart`}
                        className="p-1 rounded text-slate-muted hover:text-accent-crimson hover:bg-white transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                      <span className="text-xs font-mono font-semibold text-navy mt-4 tabular-nums">
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
            <div className="p-6 border-t border-slate-border bg-surface-subtle space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-muted">
                  <span>Authoritative Subtotal</span>
                  <span className="font-mono text-navy font-medium tabular-nums">
                    ${totalAmount.toFixed(2)} {currency}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-muted">
                  <span>Estimated Tax (Sandbox)</span>
                  <span className="font-mono text-navy font-medium tabular-nums">$0.00 {currency}</span>
                </div>
                <div className="pt-2 border-t border-slate-border flex items-baseline justify-between">
                  <span className="text-xs uppercase font-mono tracking-wider font-semibold text-navy">
                    Order Total
                  </span>
                  <div className="text-right">
                    <span className="font-serif text-2xl text-navy font-normal tabular-nums">
                      ${totalAmount.toFixed(2)}
                    </span>
                    <span className="text-xs font-mono text-slate-muted ml-1.5">
                      {currency}
                    </span>
                  </div>
                </div>
              </div>

              {/* PayPal Button Wrapper with Zero Overlapping Overlays */}
              {paymentConfig && (
                <div className="pt-2 border-t border-slate-line">
                  <PayPalButtonWrapper
                    config={paymentConfig}
                    cartItems={cartItems}
                    onSuccess={(result) => {
                      onClearCart();
                      onClose();
                      onCheckoutSuccess(result);
                    }}
                    onCancel={() => {
                      setCheckoutError('Checkout cancelled by buyer.');
                      onCheckoutCancel();
                    }}
                    onError={(err) => setCheckoutError(err)}
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
