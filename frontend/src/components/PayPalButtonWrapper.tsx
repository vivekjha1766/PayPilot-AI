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

  // If credentials are not configured, display explicit setup message without fake buttons
  if (!config.is_configured || !config.client_id) {
    return (
      <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-5 space-y-3">
        <div className="flex items-start gap-3">
          <Key className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-xs font-semibold text-amber-300 uppercase tracking-wider">
              PayPal Sandbox Setup Required
            </h4>
            <p className="text-xs text-amber-200/90 mt-1 leading-relaxed">
              No client secret or simulated payment is used in PayPilot AI. To enable the real PayPal Sandbox checkout buttons, set your credentials in <code className="px-1.5 py-0.5 bg-amber-950 rounded text-amber-100 font-mono text-[11px]">backend/.env</code>:
            </p>
            <div className="mt-2.5 p-3 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-[11px] text-slate-300 space-y-1">
              <div>PAYPAL_CLIENT_ID=&lt;your_sandbox_client_id&gt;</div>
              <div>PAYPAL_CLIENT_SECRET=&lt;your_sandbox_client_secret&gt;</div>
              <div>PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com</div>
            </div>
            <p className="text-[11px] text-amber-400/80 mt-2">
              All backend endpoints, stock validation, price calculations, and capture logic are fully tested and ready.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const handleCreateOrder = async (): Promise<string> => {
    setIsProcessing(true);
    setStatusMessage('Creating order on server with authoritative prices...');
    try {
      const orderPayload = cartItems.map((item) => ({
        sku: item.sku,
        quantity: item.quantity,
      }));

      const order = await createBackendOrder(orderPayload);
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
    setStatusMessage('Buyer approved. Server capturing payment via PayPal Sandbox...');

    try {
      const captureResult = await captureBackendOrder(internalOrderId);
      setIsProcessing(false);
      setStatusMessage(null);
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
    <div className="space-y-4">
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span className="flex items-center gap-1.5 text-emerald-400">
          <ShieldCheck className="w-4 h-4" />
          Genuine PayPal Sandbox Integration
        </span>
        <span>Orders v2 REST API</span>
      </div>

      {isProcessing && (
        <div className="rounded-xl border border-indigo-500/30 bg-indigo-500/10 p-3.5 flex items-center gap-3">
          <Loader2 className="w-4 h-4 text-indigo-400 animate-spin shrink-0" />
          <span className="text-xs text-indigo-200 font-medium">{statusMessage}</span>
        </div>
      )}

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
