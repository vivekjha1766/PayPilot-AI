export interface PaymentConfig {
  client_id: string;
  currency: string;
  is_configured: boolean;
  sandbox: boolean;
}

export interface OrderItemSnapshot {
  id: number;
  catalog_item_id: number;
  sku: string;
  name: string;
  quantity: number;
  unit_price: string;
  total_price: string;
}

export interface AuditLogItem {
  id: number;
  event_type: string;
  actor: string;
  payload: Record<string, any>;
  created_at: string;
}

export interface Order {
  id: string;
  status: 'CREATED' | 'APPROVED' | 'CAPTURING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  total_amount: string;
  currency: string;
  paypal_order_id?: string;
  paypal_capture_id?: string;
  client_idempotency_key?: string;
  items: OrderItemSnapshot[];
  audit_logs: AuditLogItem[];
  created_at: string;
  updated_at: string;
}

export interface CaptureResult {
  order_id: string;
  status: string;
  paypal_order_id: string;
  paypal_capture_id: string;
  captured_amount: string;
  currency: string;
  captured_at?: string;
}

export interface CartItem {
  sku: string;
  name: string;
  quantity: number;
  unit_price: string;
  currency: string;
  stock: number;
  category: string;
}
