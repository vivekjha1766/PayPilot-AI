import type { CatalogItem, HealthStatus } from '../types/catalog';
import type { CaptureResult, Order, PaymentConfig } from '../types/order';

let currentApiBaseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function getApiBaseUrl(): string {
  return currentApiBaseUrl;
}

export async function fetchHealth(): Promise<HealthStatus> {
  const candidates = [
    currentApiBaseUrl,
    currentApiBaseUrl.includes(':8000') ? 'http://127.0.0.1:8001' : 'http://127.0.0.1:8000',
  ];

  let lastError: Error | null = null;

  for (const url of candidates) {
    try {
      const response = await fetch(`${url}/health`);
      if (response.ok) {
        const data = await response.json();
        if (data.app === 'PayPilot AI') {
          currentApiBaseUrl = url;
          return data;
        }
      }
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));
    }
  }

  throw new Error(
    `PayPilot AI backend not responding on port 8000 or 8001 (${lastError?.message || 'Connection refused'}).`
  );
}

export async function fetchCatalog(): Promise<CatalogItem[]> {
  const response = await fetch(`${currentApiBaseUrl}/api/v1/catalog`);
  if (!response.ok) {
    throw new Error(`Failed to load catalog: HTTP ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export async function fetchPaymentConfig(): Promise<PaymentConfig> {
  const response = await fetch(`${currentApiBaseUrl}/api/v1/payments/config`);
  if (!response.ok) {
    throw new Error(`Failed to load payment config: HTTP ${response.status}`);
  }
  return response.json();
}

export async function createBackendOrder(
  items: { sku: string; quantity: number }[]
): Promise<Order> {
  const response = await fetch(`${currentApiBaseUrl}/api/v1/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Order creation failed: HTTP ${response.status}`);
  }

  return response.json();
}

export async function captureBackendOrder(orderId: string): Promise<CaptureResult> {
  const response = await fetch(`${currentApiBaseUrl}/api/v1/orders/${orderId}/capture`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Payment capture failed: HTTP ${response.status}`);
  }

  return response.json();
}

export async function cancelBackendOrder(orderId: string): Promise<Order> {
  const response = await fetch(`${currentApiBaseUrl}/api/v1/orders/${orderId}/cancel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Order cancellation failed: HTTP ${response.status}`);
  }

  return response.json();
}

export async function fetchOrderDetails(orderId: string): Promise<Order> {
  const response = await fetch(`${currentApiBaseUrl}/api/v1/orders/${orderId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch order details: HTTP ${response.status}`);
  }
  return response.json();
}
