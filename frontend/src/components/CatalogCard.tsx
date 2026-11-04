import React from 'react';
import type { CatalogItem } from '../types/catalog';
import {
  Armchair,
  Monitor,
  Keyboard,
  Headphones,
  Laptop,
  SunMedium,
  Layers,
  Check,
  Plus,
} from 'lucide-react';

interface CatalogCardProps {
  item: CatalogItem;
  quantityInCart: number;
  onAddToCart: (item: CatalogItem) => void;
}

function getCategoryIcon(category: string) {
  const norm = category.toLowerCase();
  if (norm.includes('seat') || norm.includes('chair')) {
    return <Armchair className="w-8 h-8 text-slate-muted group-hover:text-blue-primary transition-colors stroke-[1.25]" />;
  }
  if (norm.includes('display') || norm.includes('monitor')) {
    return <Monitor className="w-8 h-8 text-slate-muted group-hover:text-blue-primary transition-colors stroke-[1.25]" />;
  }
  if (norm.includes('peripheral') || norm.includes('keyboard')) {
    return <Keyboard className="w-8 h-8 text-slate-muted group-hover:text-blue-primary transition-colors stroke-[1.25]" />;
  }
  if (norm.includes('audio') || norm.includes('headset')) {
    return <Headphones className="w-8 h-8 text-slate-muted group-hover:text-blue-primary transition-colors stroke-[1.25]" />;
  }
  if (norm.includes('connect') || norm.includes('dock')) {
    return <Laptop className="w-8 h-8 text-slate-muted group-hover:text-blue-primary transition-colors stroke-[1.25]" />;
  }
  if (norm.includes('light') || norm.includes('lamp')) {
    return <SunMedium className="w-8 h-8 text-slate-muted group-hover:text-blue-primary transition-colors stroke-[1.25]" />;
  }
  return <Layers className="w-8 h-8 text-slate-muted group-hover:text-blue-primary transition-colors stroke-[1.25]" />;
}

export const CatalogCard: React.FC<CatalogCardProps> = ({
  item,
  quantityInCart,
  onAddToCart,
}) => {
  const isOutOfStock = item.stock <= 0;
  const isMaxInCart = quantityInCart >= item.stock;

  return (
    <article className="group bg-white rounded border border-slate-border hover:border-blue-primary/50 transition-colors flex flex-col justify-between overflow-hidden shadow-xs">
      {/* Product Image / Architectural Visual Frame */}
      <div className="relative aspect-[4/3] bg-surface-subtle border-b border-slate-border flex items-center justify-center p-6 transition-colors group-hover:bg-blue-soft/30">
        <div className="transform transition-transform duration-300 group-hover:scale-105">
          {getCategoryIcon(item.category)}
        </div>

        {/* Top Badges */}
        <div className="absolute top-3 left-3">
          <span className="inline-block px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider bg-white/95 border border-slate-border text-navy-soft">
            {item.category}
          </span>
        </div>

        <div className="absolute top-3 right-3">
          <span className="font-mono text-[10px] text-slate-muted tracking-tight">
            {item.sku}
          </span>
        </div>

        {/* Stock Status Pill */}
        <div className="absolute bottom-3 right-3">
          {isOutOfStock ? (
            <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-accent-crimson-bg text-accent-crimson border border-accent-crimson-border">
              Out of stock
            </span>
          ) : item.stock <= 5 ? (
            <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-accent-amber-bg text-accent-amber border border-accent-amber-border">
              {item.stock} left in stock
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-white/95 text-slate-muted border border-slate-border">
              {item.stock} in stock
            </span>
          )}
        </div>
      </div>

      {/* Details & Copy */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        <div>
          <h3 className="font-sans font-semibold text-base text-navy tracking-tight line-clamp-1 group-hover:text-blue-primary transition-colors">
            {item.name}
          </h3>
          <p className="mt-2 text-xs text-slate-muted leading-relaxed line-clamp-2">
            {item.description}
          </p>
        </div>

        {/* Pricing and Action */}
        <div className="mt-6 pt-4 border-t border-slate-line">
          <div className="flex items-baseline justify-between mb-3.5">
            <div>
              <span className="text-[10px] uppercase font-mono tracking-widest text-slate-muted block">
                Unit Price
              </span>
              <div className="flex items-baseline gap-1 mt-0.5">
                <span className="text-xl font-semibold text-navy tabular-nums tracking-tight font-sans">
                  ${item.unit_price}
                </span>
                <span className="text-xs font-mono text-slate-muted">
                  {item.currency}
                </span>
              </div>
            </div>

            {quantityInCart > 0 && (
              <span className="text-[11px] font-mono text-blue-dark">
                In Order: <strong className="text-blue-primary font-semibold">{quantityInCart}</strong>
              </span>
            )}
          </div>

          <button
            onClick={() => onAddToCart(item)}
            disabled={isOutOfStock || isMaxInCart}
            type="button"
            aria-label={`Add ${item.name} to purchase order`}
            className={`w-full py-2.5 px-4 rounded text-xs font-medium flex items-center justify-center gap-1.5 transition-colors ${
              quantityInCart > 0
                ? 'bg-blue-soft border border-blue-border text-blue-dark hover:bg-blue-soft/80'
                : 'bg-blue-primary hover:bg-blue-hover text-white shadow-xs'
            } disabled:opacity-40 disabled:cursor-not-allowed`}
          >
            {quantityInCart > 0 ? (
              <>
                <Check className="w-3.5 h-3.5 text-accent-forest" />
                <span>In Order ({quantityInCart}) • Add More</span>
              </>
            ) : isOutOfStock ? (
              <span>Out of Stock</span>
            ) : (
              <>
                <Plus className="w-3.5 h-3.5" />
                <span>Add to Order</span>
              </>
            )}
          </button>
        </div>
      </div>
    </article>
  );
};
