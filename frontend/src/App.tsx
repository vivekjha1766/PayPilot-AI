import { useEffect, useState, useCallback } from 'react';
import type { CatalogItem, HealthStatus } from './types/catalog';
import type { CartItem, CaptureResult, Order, PaymentConfig } from './types/order';
import type { AssistantStatus } from './types/assistant';
import {
  fetchCatalog,
  fetchHealth,
  fetchOrders,
  fetchPaymentConfig,
  fetchAssistantStatus,
  getApiBaseUrl,
} from './services/api';
import { Navbar } from './components/Navbar';
import { CatalogCard } from './components/CatalogCard';
import { CheckoutDrawer } from './components/CheckoutDrawer';
import { ReceiptModal } from './components/ReceiptModal';
import { TransactionHistoryModal } from './components/TransactionHistoryModal';
import { AIPurchasingAssistant } from './components/AIPurchasingAssistant';
import {
  Package,
  Search,
  RefreshCw,
  ShieldCheck,
  CheckCircle2,
  Lock,
  ArrowRight,
  X,
} from 'lucide-react';

export function App() {
  const [catalog, setCatalog] = useState<CatalogItem[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [paymentConfig, setPaymentConfig] = useState<PaymentConfig | null>(null);
  const [assistantStatus, setAssistantStatus] = useState<AssistantStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  // Cart & Checkout State
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState<boolean>(false);
  const [orders, setOrders] = useState<Order[]>([]);
  const [historyLoading, setHistoryLoading] = useState<boolean>(false);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);
  const [completedCapture, setCompletedCapture] = useState<CaptureResult | null>(null);

  const loadOrders = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const orderList = await fetchOrders();
      setOrders(orderList);
    } catch {
      // Ignore background order fetch failure
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const refreshData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Await fetchHealth first to dynamically determine and set active backend port
      const healthData = await fetchHealth();
      setHealth(healthData);

      const [catalogData, payConfig, aiStatus] = await Promise.all([
        fetchCatalog(),
        fetchPaymentConfig(),
        fetchAssistantStatus().catch(() => null),
      ]);
      setCatalog(catalogData);
      setPaymentConfig(payConfig);
      setAssistantStatus(aiStatus);
      await loadOrders();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown connection error';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [loadOrders]);

  useEffect(() => {
    let isCancelled = false;
    async function init() {
      try {
        const healthData = await fetchHealth();
        if (!isCancelled) setHealth(healthData);

        const [catalogData, payConfig, aiStatus] = await Promise.all([
          fetchCatalog(),
          fetchPaymentConfig(),
          fetchAssistantStatus().catch(() => null),
        ]);

        if (!isCancelled) {
          setCatalog(catalogData);
          setPaymentConfig(payConfig);
          setAssistantStatus(aiStatus);
          const orderList = await fetchOrders().catch(() => []);
          setOrders(orderList);

          const params = new URLSearchParams(window.location.search);
          if (params.get('view') === 'history') {
            setIsHistoryOpen(true);
          } else if (params.get('view') === 'cart') {
            if (catalogData.length > 0) {
              const item = catalogData[0];
              setCartItems([{
                sku: item.sku,
                name: item.name,
                quantity: 1,
                unit_price: item.unit_price,
                currency: item.currency,
                stock: item.stock,
                category: item.category,
              }]);
            }
            setIsDrawerOpen(true);
          }
          if (params.get('category')) {
            setSelectedCategory(params.get('category')!);
          }
          if (params.get('search')) {
            setSearchQuery(params.get('search')!);
          }
        }
      } catch (err: unknown) {
        if (!isCancelled) {
          const message = err instanceof Error ? err.message : 'Unknown connection error';
          setError(message);
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }
    init();
    return () => {
      isCancelled = true;
    };
  }, []);

  const handleAddPlanItemsToCart = (items: { sku: string; quantity: number }[]) => {
    setCartItems((prev) => {
      const nextCart = [...prev];
      for (const planItem of items) {
        const catItem = catalog.find((c) => c.sku === planItem.sku);
        if (!catItem) continue;
        const existingIndex = nextCart.findIndex((i) => i.sku === planItem.sku);
        if (existingIndex >= 0) {
          const newQty = Math.min(catItem.stock, nextCart[existingIndex].quantity + planItem.quantity);
          nextCart[existingIndex] = { ...nextCart[existingIndex], quantity: newQty };
        } else {
          nextCart.push({
            sku: catItem.sku,
            name: catItem.name,
            quantity: Math.min(catItem.stock, planItem.quantity),
            unit_price: catItem.unit_price,
            currency: catItem.currency,
            stock: catItem.stock,
            category: catItem.category,
          });
        }
      }
      return nextCart;
    });
  };

  const handleAddToCart = (item: CatalogItem) => {
    setCartItems((prev) => {
      const existing = prev.find((i) => i.sku === item.sku);
      if (existing) {
        if (existing.quantity >= item.stock) return prev;
        return prev.map((i) =>
          i.sku === item.sku ? { ...i, quantity: i.quantity + 1 } : i
        );
      }
      return [
        ...prev,
        {
          sku: item.sku,
          name: item.name,
          quantity: 1,
          unit_price: item.unit_price,
          currency: item.currency,
          stock: item.stock,
          category: item.category,
        },
      ];
    });
    setIsDrawerOpen(true);
  };

  const handleUpdateQuantity = (sku: string, delta: number) => {
    setCartItems((prev) =>
      prev
        .map((item) => {
          if (item.sku === sku) {
            const nextQty = item.quantity + delta;
            if (nextQty <= 0) return null;
            if (nextQty > item.stock) return item;
            return { ...item, quantity: nextQty };
          }
          return item;
        })
        .filter((item): item is CartItem => item !== null)
    );
  };

  const handleRemoveItem = (sku: string) => {
    setCartItems((prev) => prev.filter((i) => i.sku !== sku));
  };

  const handleClearCart = () => {
    setCartItems([]);
  };

  const cartTotalAmount = cartItems
    .reduce((sum, item) => sum + parseFloat(item.unit_price) * item.quantity, 0)
    .toFixed(2);
  const cartItemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  const categories = ['ALL', ...Array.from(new Set(catalog.map((i) => i.category)))];

  const filteredItems = catalog.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = selectedCategory === 'ALL' || item.category === selectedCategory;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="min-h-screen bg-canvas text-navy flex flex-col font-sans">
      {/* Refined Minimalist Navbar */}
      <Navbar
        health={health}
        error={error}
        cartCount={cartItemCount}
        cartTotal={cartTotalAmount}
        onOpenCart={() => setIsDrawerOpen(true)}
        onOpenHistory={() => setIsHistoryOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-10">
        {/* Generous Editorial Hero Section */}
        <section className="bg-white rounded border border-slate-border p-8 sm:p-12 space-y-8 shadow-xs">
          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded border border-blue-border bg-blue-soft text-blue-dark text-xs font-mono font-medium">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-primary" />
              <span>PayPal Sandbox Orders v2 REST API</span>
            </div>
            <h1 className="font-serif text-3xl sm:text-5xl text-navy font-normal tracking-tight leading-[1.15]">
              Curated Merchant Equipment &amp; Intelligent Purchasing
            </h1>
            <p className="text-slate-muted text-sm sm:text-base leading-relaxed">
              Select verified hardware from the authoritative merchant catalog, evaluate procurement proposals with the purchasing assistant, and settle transactions through PayPal Orders v2 with cryptographic integrity.
            </p>
          </div>

          {/* Understated Governance Metrics Strip */}
          <div className="pt-6 border-t border-slate-line grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded border border-slate-border bg-canvas/60 space-y-1">
              <div className="flex items-center gap-1.5 font-medium text-navy">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-forest" />
                <span className="font-mono text-[11px] uppercase tracking-wider">Deterministic Catalog</span>
              </div>
              <p className="text-slate-muted text-[11px] leading-relaxed">
                Authoritative SQLite inventory with strict stock reservation and decimal unit pricing.
              </p>
            </div>

            <div className="p-4 rounded border border-slate-border bg-canvas/60 space-y-1">
              <div className="flex items-center gap-1.5 font-medium text-navy">
                <Lock className="w-3.5 h-3.5 text-blue-primary" />
                <span className="font-mono text-[11px] uppercase tracking-wider">Server-Side Capture</span>
              </div>
              <p className="text-slate-muted text-[11px] leading-relaxed">
                OAuth 2.0 PayPal token exchange, idempotency keys, and immutable order audit records.
              </p>
            </div>

            <div className="p-4 rounded border border-slate-border bg-canvas/60 space-y-1">
              <div className="flex items-center gap-1.5 font-medium text-navy">
                <ArrowRight className="w-3.5 h-3.5 text-blue-primary" />
                <span className="font-mono text-[11px] uppercase tracking-wider">Advisory Consultant</span>
              </div>
              <p className="text-slate-muted text-[11px] leading-relaxed">
                Gemini-powered intent evaluation grounded strictly against live warehouse stock.
              </p>
            </div>
          </div>
        </section>

        {/* AI Purchasing Assistant (Quiet Shopping Consultant) */}
        <AIPurchasingAssistant
          onAddItemsToCart={handleAddPlanItemsToCart}
          onOpenCart={() => setIsDrawerOpen(true)}
          isConfigured={assistantStatus?.is_configured ?? false}
          configuredModel={assistantStatus?.configured_model}
          fallbackModel={assistantStatus?.fallback_model}
        />

        {/* Storefront Catalog Section */}
        <section className="space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-baseline justify-between gap-2 pb-2 border-b border-slate-line">
            <div>
              <h2 className="font-serif text-2xl text-navy font-normal tracking-tight">
                Authoritative Merchant Catalog
              </h2>
              <p className="text-xs text-slate-muted mt-0.5">
                Real-time stock levels and certified unit pricing
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="font-mono text-[11px] text-slate-muted">
                Endpoint: <span className="text-navy font-medium">{getApiBaseUrl()}</span>
              </span>
              <button
                onClick={refreshData}
                disabled={loading}
                type="button"
                aria-label="Refresh catalog data"
                title="Refresh catalog data"
                className="p-1.5 rounded border border-slate-border bg-white hover:bg-blue-soft/50 hover:border-blue-border hover:text-blue-primary text-slate-muted transition-colors disabled:opacity-40"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          {/* Catalog Controls: Search and Filters */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="relative flex-1 sm:max-w-md">
              <Search className="w-3.5 h-3.5 text-slate-muted absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search catalog by name, description, or SKU..."
                className="w-full pl-9 pr-8 py-2 rounded border border-slate-border bg-white text-xs text-navy placeholder-slate-muted focus:border-blue-primary focus:outline-none transition-colors"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  aria-label="Clear search query"
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 p-0.5 text-slate-muted hover:text-navy rounded transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>

            {/* Category Filter Tabs */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
              {categories.map((cat) => {
                const isActive = selectedCategory === cat;
                return (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    type="button"
                    className={`text-xs px-3 py-1.5 rounded font-mono transition-colors whitespace-nowrap ${
                      isActive
                        ? 'bg-blue-primary text-white font-medium shadow-xs'
                        : 'bg-white text-slate-muted hover:text-blue-primary hover:bg-blue-soft/50 border border-slate-border'
                    }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Connection Error Banner */}
          {error && (
            <div className="rounded p-4 bg-accent-crimson-bg border border-accent-crimson-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs">
              <div>
                <h3 className="font-semibold text-accent-crimson">
                  Unable to connect to FastAPI backend at {getApiBaseUrl()}
                </h3>
                <p className="text-navy-soft mt-1 leading-relaxed">
                  Verify the backend process is running locally:
                  <code className="ml-1.5 px-1.5 py-0.5 rounded bg-white border border-accent-crimson-border font-mono text-[11px] text-navy">
                    uvicorn app.main:app --port 8000
                  </code>
                </p>
              </div>
              <button
                onClick={refreshData}
                type="button"
                className="px-4 py-2 rounded bg-blue-primary hover:bg-blue-hover text-white font-medium transition-colors shrink-0"
              >
                Retry Connection
              </button>
            </div>
          )}

          {/* Loading Skeleton */}
          {loading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {Array.from({ length: 8 }).map((_, idx) => (
                <div
                  key={idx}
                  className="rounded border border-slate-border bg-white p-5 space-y-4 animate-pulse"
                >
                  <div className="aspect-[4/3] bg-surface-subtle rounded border border-slate-line" />
                  <div className="h-4 bg-surface-subtle rounded w-3/4" />
                  <div className="h-3 bg-surface-subtle rounded w-full" />
                  <div className="h-3 bg-surface-subtle rounded w-2/3" />
                  <div className="h-8 bg-surface-subtle rounded w-full pt-4" />
                </div>
              ))}
            </div>
          )}

          {/* Catalog Grid */}
          {!loading && !error && filteredItems.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {filteredItems.map((item) => {
                const inCart = cartItems.find((i) => i.sku === item.sku);
                return (
                  <CatalogCard
                    key={item.id}
                    item={item}
                    quantityInCart={inCart ? inCart.quantity : 0}
                    onAddToCart={handleAddToCart}
                  />
                );
              })}
            </div>
          )}

          {/* Empty Catalog Filter State */}
          {!loading && !error && filteredItems.length === 0 && (
            <div className="rounded border border-slate-border bg-white p-12 text-center space-y-3">
              <Package className="w-10 h-10 text-slate-muted mx-auto stroke-[1.25]" />
              <h3 className="font-serif text-lg text-navy font-normal">No items match your criteria</h3>
              <p className="text-xs text-slate-muted max-w-sm mx-auto leading-relaxed">
                Adjust your search query or reset category filters to view all catalog items.
              </p>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('ALL');
                }}
                type="button"
                className="inline-block mt-2 text-xs font-mono font-medium text-blue-primary underline underline-offset-4 hover:text-blue-hover"
              >
                Reset Filters
              </button>
            </div>
          )}
        </section>
      </main>

      {/* Slide-out Checkout Drawer */}
      <CheckoutDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        cartItems={cartItems}
        onUpdateQuantity={handleUpdateQuantity}
        onRemoveItem={handleRemoveItem}
        onClearCart={handleClearCart}
        paymentConfig={paymentConfig}
        onCheckoutSuccess={(result) => {
          setCompletedCapture(result);
          refreshData(); // reload catalog to reflect updated stock!
        }}
        onCheckoutCancel={() => {
          // Keep cart intact so buyer can retry
        }}
        checkoutError={checkoutError}
        setCheckoutError={setCheckoutError}
      />

      {/* Settlement Receipt Modal */}
      <ReceiptModal
        result={completedCapture}
        onClose={() => setCompletedCapture(null)}
      />

      {/* Transaction History & Audit Trail Modal */}
      <TransactionHistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        orders={orders}
        onRefresh={loadOrders}
        loading={historyLoading}
      />

      {/* Refined Minimalist Editorial Footer */}
      <footer className="border-t border-slate-border bg-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-muted">
          <div className="flex items-center gap-2">
            <span className="font-serif font-semibold text-navy text-sm">PayPilot</span>
            <span className="text-slate-border">•</span>
            <span>Enterprise Hardened Purchasing &amp; Settlement Operations</span>
          </div>
          <div className="font-mono text-[11px] text-slate-muted">
            PayPal Orders v2 REST API • Google Gemini Advisory
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
