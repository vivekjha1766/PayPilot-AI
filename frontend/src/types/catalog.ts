export interface CatalogItem {
  id: number;
  sku: string;
  name: string;
  description: string;
  unit_price: string; // Serialized decimal string e.g. "289.50"
  currency: string;
  stock: number;
  category: string;
}

export interface HealthStatus {
  status: string;
  app: string;
  environment: string;
  version: string;
}
