import type { CatalogItem } from '../types/catalog';
import { Box, Layers } from 'lucide-react';

interface CatalogCardProps {
  item: CatalogItem;
}

export const CatalogCard: React.FC<CatalogCardProps> = ({ item }) => {
  return (
    <div className="group rounded-2xl border border-slate-800 bg-slate-900/60 hover:bg-slate-900 hover:border-slate-700 transition-all duration-200 p-6 flex flex-col justify-between shadow-sm hover:shadow-xl hover:shadow-indigo-500/5">
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700/60">
            <Layers className="w-3 h-3 text-indigo-400" />
            {item.category}
          </span>
          <span className="text-[11px] font-mono text-slate-400 bg-slate-950/60 px-2 py-0.5 rounded border border-slate-800/80">
            SKU: {item.sku}
          </span>
        </div>

        <h3 className="text-base font-semibold text-white group-hover:text-indigo-300 transition-colors line-clamp-1">
          {item.name}
        </h3>

        <p className="mt-2 text-xs text-slate-400 leading-relaxed line-clamp-3">
          {item.description}
        </p>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between">
        <div>
          <span className="text-[10px] uppercase font-semibold text-slate-400 block tracking-wider">
            Authoritative Unit Price
          </span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-xl font-bold text-white tracking-tight">
              ${item.unit_price}
            </span>
            <span className="text-xs font-medium text-slate-400">
              {item.currency}
            </span>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] uppercase font-semibold text-slate-400 block tracking-wider">
            Stock
          </span>
          <div className="flex items-center gap-1.5 mt-0.5 justify-end">
            <Box className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-xs font-semibold text-emerald-300">
              {item.stock} in stock
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
