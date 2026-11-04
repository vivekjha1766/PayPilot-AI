import React, { useState } from 'react';
import { PayPalScriptProvider, PayPalButtons } from '@paypal/react-paypal-js';
import type { CartItem, CaptureResult, PaymentConfig } from '../types/order';
import { createBackendOrder, captureBackendOrder, cancelBackendOrder } from '../services/api';
import { Key, Loader2, ShieldCheck } from 'lucide-react';

interface PayPalButtonWrapperProps {
  config: PaymentConfig;
  cartItems: CartItem[];
  onSuccess: (result: CaptureResult) => void;
  onCancel: () => void;
  onError: (error: string) => void;
}

export const PayPalButtonWrapper: React.FC<PayPalButtonWrapperProps> = ({
  config,
  cartItems,
  onSuccess,
  onCancel,
  onError,
}) => {
  const [internalOrderId, setInternalOrderId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [checkoutKey, setCheckoutKey] = useState<string>(() => crypto.randomUUID());

  // Regenerate idempotency key when cart composition changes
  const cartSignature = cartItems.map((i) => `${i.sku}:${i.quantity}`).join(',');
  const prevSignatureRef = React.useRef(cartSignature);
  React.useEffect(() => {
    if (prevSignatureRef.current !== cartSignature) {
      prevSignatureRef.current = cartSignature;
      setCheckoutKey(crypto.randomUUID());
      setInternalOrderId(null);
    }
  }, [cartSignature]);

  // If credentials are not configured, display explicit setup message without fake buttons
  if (!config.is_configured || !config.client_id) {
    return (
      <div className="rounded border border-accent-amber-border bg-accent-amber-bg p-4 space-y-2.5">
        <div className="flex items-start gap-2.5">
          <Key className="w-4 h-4 text-accent-amber shrink-0 mt-0.5" />
          <div className="text-xs">
            <h4 className="font-semibold text-accent-amber uppercase tracking-wider text-[11px]">
              PayPal Sandbox Configuration Required
            </h4>
            <p className="text-navy-soft mt-1 leading-relaxed text-[11px]">
              Set your sandbox credentials in <code className="px-1 py-0.5 bg-white rounded border border-accent-amber-border font-mono text-[10px]">backend/.env</code> to activate live PayPal checkout:
            </p>
            <div className="mt-2 p-2.5 rounded bg-white border border-slate-border font-mono text-[10px] text-navy space-y-0.5">
              <div>PAYPAL_CLIENT_ID=&lt;your_sandbox_client_id&gt;</div>
              <div>PAYPAL_CLIENT_SECRET=&lt;your_sandbox_client_secret&gt;</div>
              <div>PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com</div>
            </div>
            <p className="text-[10px] text-slate-muted mt-2">
              All backend endpoints, stock validation, and capture verification are active and tested.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const handleCreateOrder = async (): Promise<string> => {
    setIsProcessing(true);
    setStatusMessage('Initiating order with server-verified prices...');
    try {
      const orderPayload = cartItems.map((item) => ({
        sku: item.sku,
        quantity: item.quantity,
      }));

      // Pass stable checkoutKey to guarantee client idempotency across network retries
      const order = await createBackendOrder(orderPayload, checkoutKey);
      setInternalOrderId(order.id);
      setStatusMessage('Order created. Awaiting buyer sandbox approval...');

      if (!order.paypal_order_id) {
        throw new Error('Backend failed to return a valid PayPal order ID.');
      }

      return order.paypal_order_id;
    } catch (err) {
      setIsProcessing(false);
      setStatusMessage(null);
      const msg = err instanceof Error ? err.message : 'Failed to create order on server';
      onError(msg);
      throw err;
    }
  };

  const handleApprove = async (_data: Record<string, any>): Promise<void> => {
    if (!internalOrderId) {
      onError('Internal order ID was lost during approval callback.');
      return;
    }

    setIsProcessing(true);
    setStatusMessage('Buyer approved. Capturing payment via PayPal Sandbox...');

    try {
      const captureResult = await captureBackendOrder(internalOrderId);
      setIsProcessing(false);
      setStatusMessage(null);
      setCheckoutKey(crypto.randomUUID());
      onSuccess(captureResult);
    } catch (err) {
      setIsProcessing(false);
      setStatusMessage(null);
      const msg = err instanceof Error ? err.message : 'Server capture failed';
      onError(msg);
    }
  };

  const handleCancel = async (_data: Record<string, any>): Promise<void> => {
    setIsProcessing(false);
    setStatusMessage(null);
    if (internalOrderId) {
      try {
        await cancelBackendOrder(internalOrderId);
      } catch {
        // Ignore cancellation error
      }
    }
    onCancel();
  };

  const handleError = (err: Record<string, any>): void => {
    setIsProcessing(false);
    setStatusMessage(null);
    onError(err?.message || 'PayPal Sandbox encountered an unexpected error.');
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-[11px] text-slate-muted px-0.5">
        <span className="flex items-center gap-1.5 text-navy-soft">
          <ShieldCheck className="w-3.5 h-3.5 text-blue-primary" />
          <span>PayPal Orders v2</span>
        </span>
        <span className="font-mono text-[10px]">Server Capture</span>
      </div>

      {isProcessing && (
        <div className="rounded p-3 bg-blue-soft border border-blue-border flex items-center gap-2.5">
          <Loader2 className="w-3.5 h-3.5 text-blue-primary animate-spin shrink-0" />
          <span className="text-xs text-blue-dark font-medium">{statusMessage}</span>
        </div>
      )}

      {/* Real PayPal Buttons container with clean relative stacking and zero overlapping overlays */}
      <PayPalScriptProvider
        options={{
          clientId: config.client_id,
          currency: config.currency,
          intent: 'capture',
        }}
      >
        <div className="relative z-0">
          <PayPalButtons
            style={{
              layout: 'vertical',
              color: 'gold',
              shape: 'rect',
              label: 'pay',
              height: 44,
            }}
            disabled={isProcessing || cartItems.length === 0}
            createOrder={handleCreateOrder}
            onApprove={handleApprove}
            onCancel={handleCancel}
            onError={handleError}
          />
        </div>
      </PayPalScriptProvider>
    </div>
  );
};
