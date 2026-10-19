import type { CatalogItem, HealthStatus } from '../types/catalog';

// Default to configured VITE_API_URL or 8000 with dynamic 8001 fallback if 8000 is occupied
let currentApiBaseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function getApiBaseUrl(): string {
  return currentApiBaseUrl;
}

export async function fetchHealth(): Promise<HealthStatus> {
  // Try candidate URLs to detect the PayPilot AI backend
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
