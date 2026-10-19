import { useEffect, useState } from 'react';
import type { CatalogItem, HealthStatus } from './types/catalog';
import { fetchCatalog, fetchHealth, getApiBaseUrl } from './services/api';
import { Navbar } from './components/Navbar';
import { CatalogCard } from './components/CatalogCard';
import {
  Package,
  Search,
  RefreshCw,
  Database,
} from 'lucide-react';

export function App() {
  const [catalog, setCatalog] = useState<CatalogItem[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthData, catalogData] = await Promise.all([
        fetchHealth(),
        fetchCatalog(),
      ]);
      setHealth(healthData);
      setCatalog(catalogData);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown connection error';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

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
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Navbar health={health} error={error} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section */}
        <div className="rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900/90 to-indigo-950/40 p-8 sm:p-10 relative overflow-hidden shadow-2xl">
          <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold">
              <Database className="w-3.5 h-3.5" />
              Verified Authoritative Merchant Catalog
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              AI Purchasing Agent & Payment Operations
            </h1>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              PayPilot AI bridges natural language enterprise purchasing with strict server-side validation and genuine PayPal Sandbox execution. This catalog forms the immutable source of truth for all agent intent reconciliation.
            </p>
          </div>

          {/* Architecture Roadmap Bar */}
          <div className="mt-8 pt-6 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start gap-3 p-3 rounded-xl bg-slate-950/60 border border-emerald-500/30">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 font-bold text-xs shrink-0">
                M1
              </div>
              <div>
                <span className="text-xs font-semibold text-emerald-400 block">Milestone 1: Active</span>
                <span className="text-[11px] text-slate-400">FastAPI, SQLite catalog, deterministic seeding & Decimal pricing</span>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 rounded-xl bg-slate-950/40 border border-slate-800">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 font-bold text-xs shrink-0">
                M2
              </div>
              <div>
                <span className="text-xs font-semibold text-slate-300 block">Milestone 2: Payments</span>
                <span className="text-[11px] text-slate-400">PayPal Sandbox Orders v2 OAuth, Create Order & Server Capture</span>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 rounded-xl bg-slate-950/40 border border-slate-800">
              <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 font-bold text-xs shrink-0">
                M3
              </div>
              <div>
                <span className="text-xs font-semibold text-slate-300 block">Milestone 3: AI Engine</span>
                <span className="text-[11px] text-slate-400">Structured prompt intent parsing & explainable risk scoring</span>
              </div>
            </div>
          </div>
        </div>

        {/* Catalog Control Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="relative flex-1 sm:w-80">
              <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search catalog by name, description or SKU..."
                className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>

            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                    selectedCategory === cat
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2 self-end sm:self-auto">
            <span className="text-xs text-slate-400 font-mono">
              Target API: <span className="text-slate-300">{getApiBaseUrl()}</span>
            </span>
            <button
              onClick={loadData}
              disabled={loading}
              title="Refresh Catalog Data"
              className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-semibold text-rose-300">
                Cannot connect to FastAPI backend at {getApiBaseUrl()}
              </h3>
              <p className="text-xs text-rose-400/90 mt-1">
                Make sure the backend is running using PowerShell:
                <code className="ml-1 px-1.5 py-0.5 rounded bg-rose-950 font-mono text-[11px] text-rose-200">
                  .\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
                </code>
              </p>
            </div>
            <button
              onClick={loadData}
              className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-xs font-semibold text-white transition-colors shrink-0"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, idx) => (
              <div
                key={idx}
                className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6 space-y-4 animate-pulse"
              >
                <div className="h-4 bg-slate-800 rounded w-1/3" />
                <div className="h-5 bg-slate-800 rounded w-3/4" />
                <div className="h-12 bg-slate-800 rounded w-full" />
                <div className="h-8 bg-slate-800 rounded w-1/2 pt-4" />
              </div>
            ))}
          </div>
        )}

        {/* Catalog Grid */}
        {!loading && !error && filteredItems.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {filteredItems.map((item) => (
              <CatalogCard key={item.id} item={item} />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && filteredItems.length === 0 && (
          <div className="rounded-3xl border border-slate-800 bg-slate-900/30 p-12 text-center space-y-3">
            <Package className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-base font-semibold text-slate-300">No items match your criteria</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Try adjusting your search query or reset the category filter to view all seeded products.
            </p>
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('ALL');
              }}
              className="mt-2 text-xs font-medium text-indigo-400 hover:text-indigo-300"
            >
              Reset Filters
            </button>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800 bg-slate-950 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-400">
          PayPilot AI — Phase 1 Prototype | PayPal Sandbox Checkout & Autonomous Agent Operations
        </div>
      </footer>
    </div>
  );
}

export default App;
