"use client";

import React, { useState, useMemo } from "react";
import { Product } from "../lib/types";
import {
  Layers,
  Search,
  Star,
  CheckCircle2,
  AlertCircle,
  XCircle,
  MessageSquarePlus,
  ChevronDown,
  Sparkles,
} from "lucide-react";

interface SidebarProps {
  products: Product[];
  isLoading: boolean;
  onSelectProductQuery?: (productName: string) => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  products,
  isLoading,
  onSelectProductQuery,
  isOpenMobile,
  onCloseMobile,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Extract unique categories
  const categories = useMemo(() => {
    const cats = new Set<string>();
    products.forEach((p) => {
      if (p.category) cats.add(p.category);
    });
    return ["All", ...Array.from(cats)];
  }, [products]);

  // Filter products by category and search query
  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      const matchesCategory =
        selectedCategory === "All" ||
        product.category.toLowerCase() === selectedCategory.toLowerCase();
      const matchesSearch =
        product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.brand.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [products, selectedCategory, searchQuery]);

  const renderStockBadge = (status: string, quantity: number) => {
    if (status === "in_stock") {
      return (
        <span className="inline-flex items-center gap-1 rounded-md border border-emerald-500/20 bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-medium text-emerald-400">
          <CheckCircle2 className="h-2.5 w-2.5" />
          <span>In Stock ({quantity})</span>
        </span>
      );
    }
    if (status === "low_stock") {
      return (
        <span className="inline-flex items-center gap-1 rounded-md border border-amber-500/20 bg-amber-500/10 px-1.5 py-0.5 text-[10px] font-medium text-amber-400">
          <AlertCircle className="h-2.5 w-2.5" />
          <span>Low Stock ({quantity})</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 rounded-md border border-rose-500/20 bg-rose-500/10 px-1.5 py-0.5 text-[10px] font-medium text-rose-400">
        <XCircle className="h-2.5 w-2.5" />
        <span>Out of Stock</span>
      </span>
    );
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex h-full min-h-0 w-80 shrink-0 flex-col border-r border-[#27272a] bg-[#121215] transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          isOpenMobile ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Top Header */}
        <div className="flex shrink-0 flex-col gap-3 border-b border-[#27272a] p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-zinc-300" />
              <h2 className="text-sm font-semibold text-zinc-100">
                Product Catalogue
              </h2>
            </div>
            <span className="rounded-md bg-zinc-800/80 px-2 py-0.5 text-[10px] font-medium text-zinc-400">
              {filteredProducts.length} items
            </span>
          </div>

          {/* Search Box */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-zinc-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search catalogue..."
              className="w-full rounded-lg border border-zinc-800 bg-[#09090b] py-2 pr-3 pl-8 text-xs text-zinc-100 placeholder-zinc-500 transition-colors focus:border-zinc-500 focus:outline-none"
            />
          </div>

          {/* Category Dropdown */}
          <div className="relative">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full appearance-none rounded-lg border border-zinc-800 bg-[#09090b] px-3 py-2 text-xs font-medium text-zinc-200 transition-colors focus:border-zinc-500 focus:outline-none"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat === "All" ? "All Categories" : cat.toUpperCase()}
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-2.5 h-3.5 w-3.5 text-zinc-400" />
          </div>
        </div>

        {/* Product Cards List */}
        <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-2.5">
          {isLoading ? (
            <div className="flex flex-col gap-2 p-2">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="h-24 animate-pulse rounded-xl border border-zinc-800 bg-zinc-900/60"
                />
              ))}
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 text-center text-xs text-zinc-500">
              <Search className="mb-2 h-6 w-6 text-zinc-600" />
              <p>No products match your filter criteria.</p>
            </div>
          ) : (
            filteredProducts.map((product) => (
              <div
                key={product.product_id}
                className="group relative flex flex-col gap-2 rounded-xl border border-zinc-800/90 bg-[#16161a] p-3 transition-all hover:border-zinc-700 hover:bg-[#1a1a20]"
              >
                {/* Header Row: Title & Stock Badge */}
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-xs font-medium text-zinc-200 group-hover:text-white">
                    {product.name}
                  </h3>
                  {renderStockBadge(
                    product.availability_status,
                    product.stock_quantity
                  )}
                </div>

                {/* Brand & Category Micro-label */}
                <div className="flex items-center gap-2 text-[10px] text-zinc-400">
                  <span className="font-medium text-zinc-300">
                    {product.brand}
                  </span>
                  <span>•</span>
                  <span className="rounded bg-[#09090b] px-1.5 py-0.5 uppercase tracking-wider text-zinc-300">
                    {product.category}
                  </span>
                </div>

                {/* Price & Rating Row */}
                <div className="mt-0.5 flex items-center justify-between">
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-sm font-semibold text-white">
                      ₹{product.price.toLocaleString("en-IN")}
                    </span>
                    {product.original_price > product.price && (
                      <>
                        <span className="text-[10px] text-zinc-500 line-through">
                          ₹{product.original_price.toLocaleString("en-IN")}
                        </span>
                        <span className="rounded bg-emerald-500/10 px-1 py-0.5 text-[10px] font-medium text-emerald-400">
                          {product.discount_percentage}% OFF
                        </span>
                      </>
                    )}
                  </div>

                  <div className="flex items-center gap-1 text-[11px] text-amber-400">
                    <Star className="h-3 w-3 fill-amber-400" />
                    <span className="font-medium">{product.rating}</span>
                    <span className="text-[10px] text-zinc-500">
                      ({product.review_count})
                    </span>
                  </div>
                </div>

                {/* Quick Query CTA button */}
                {onSelectProductQuery && (
                  <button
                    type="button"
                    onClick={() =>
                      onSelectProductQuery(
                        `Tell me more about ${product.name} and compare it with similar options.`
                      )
                    }
                    className="mt-1 flex w-full items-center justify-center gap-1.5 rounded-lg border border-zinc-700/60 bg-zinc-800/80 py-1 text-[11px] font-medium text-zinc-300 transition-all hover:bg-zinc-700 hover:text-white"
                  >
                    <MessageSquarePlus className="h-3.5 w-3.5" />
                    <span>Ask Assistant About This</span>
                  </button>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer info */}
        <div className="shrink-0 border-t border-[#27272a] bg-[#09090b] p-3 text-center text-[10px] text-zinc-500">
          <span className="flex items-center justify-center gap-1">
            <Sparkles className="h-3 w-3 text-zinc-400" />
            <span>FastAPI Catalog • Live In-Memory SQLite</span>
          </span>
        </div>
      </aside>
    </>
  );
};
