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
        <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium tracking-wider text-emerald-400 uppercase">
          <CheckCircle2 className="h-3 w-3" />
          <span>In Stock ({quantity})</span>
        </span>
      );
    }
    if (status === "low_stock") {
      return (
        <span className="inline-flex items-center gap-1 rounded-full border border-amber-500/20 bg-amber-500/10 px-2 py-0.5 text-[10px] font-medium tracking-wider text-amber-400 uppercase">
          <AlertCircle className="h-3 w-3" />
          <span>Low Stock ({quantity})</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 rounded-full border border-rose-500/20 bg-rose-500/10 px-2 py-0.5 text-[10px] font-medium tracking-wider text-rose-400 uppercase">
        <XCircle className="h-3 w-3" />
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
        className={`fixed inset-y-0 left-0 z-40 flex h-full min-h-0 w-80 shrink-0 flex-col border-r border-[#2d3345] bg-[#161922] transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          isOpenMobile ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Top Header */}
        <div className="flex shrink-0 flex-col gap-3 border-b border-[#2d3345] p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-indigo-400" />
              <h2 className="text-base font-semibold text-[#f8fafc]">
                Product Catalogue
              </h2>
            </div>
            <span className="rounded-full bg-[#1c202d] px-2 py-0.5 text-[10px] font-medium text-[#94a3b8]">
              {filteredProducts.length} items
            </span>
          </div>

          {/* Search Box */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-[#94a3b8]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search catalogue..."
              className="w-full rounded-lg border border-[#2d3345] bg-[#0f1117] py-2 pr-3 pl-9 text-xs text-[#f8fafc] placeholder-[#94a3b8] transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          {/* Category Dropdown */}
          <div className="relative">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full appearance-none rounded-lg border border-[#2d3345] bg-[#0f1117] px-3 py-2 text-xs font-medium text-[#f8fafc] transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat === "All" ? "All Categories" : cat.toUpperCase()}
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-2.5 h-4 w-4 text-[#94a3b8]" />
          </div>
        </div>

        {/* Product Cards List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {isLoading ? (
            <div className="flex flex-col gap-2 p-2">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="h-24 animate-pulse rounded-xl border border-[#2d3345] bg-[#1c202d]"
                />
              ))}
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 text-center text-xs text-[#94a3b8]">
              <Search className="mb-2 h-6 w-6 text-[#94a3b8]/50" />
              <p>No products match your filter criteria.</p>
            </div>
          ) : (
            filteredProducts.map((product) => (
              <div
                key={product.product_id}
                className="group relative flex flex-col gap-2 rounded-xl border border-[#2d3345] bg-[#1c202d] p-3 transition-all hover:border-indigo-500/50 hover:bg-[#232838] hover:shadow-md"
              >
                {/* Header Row: Title & Stock Badge */}
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-xs font-semibold text-[#f8fafc] group-hover:text-indigo-300">
                    {product.name}
                  </h3>
                  {renderStockBadge(
                    product.availability_status,
                    product.stock_quantity
                  )}
                </div>

                {/* Brand & Category Micro-label */}
                <div className="flex items-center gap-2 text-[10px] text-[#94a3b8]">
                  <span className="font-medium text-slate-300">
                    {product.brand}
                  </span>
                  <span>•</span>
                  <span className="rounded bg-[#0f1117] px-1.5 py-0.5 uppercase tracking-wider text-indigo-400">
                    {product.category}
                  </span>
                </div>

                {/* Price & Rating Row */}
                <div className="mt-1 flex items-center justify-between">
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-sm font-bold text-white">
                      ₹{product.price.toLocaleString("en-IN")}
                    </span>
                    {product.original_price > product.price && (
                      <>
                        <span className="text-[10px] text-[#94a3b8] line-through">
                          ₹{product.original_price.toLocaleString("en-IN")}
                        </span>
                        <span className="rounded bg-emerald-500/10 px-1 py-0.5 text-[10px] font-semibold text-emerald-400">
                          {product.discount_percentage}% OFF
                        </span>
                      </>
                    )}
                  </div>

                  <div className="flex items-center gap-1 text-[11px] text-amber-400">
                    <Star className="h-3 w-3 fill-amber-400" />
                    <span className="font-medium">{product.rating}</span>
                    <span className="text-[10px] text-[#94a3b8]">
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
                    className="mt-1 flex w-full items-center justify-center gap-1.5 rounded-lg border border-indigo-500/20 bg-indigo-500/10 py-1 text-[11px] font-medium text-indigo-300 opacity-90 transition-all hover:border-indigo-500 hover:bg-indigo-600 hover:text-white group-hover:opacity-100"
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
        <div className="shrink-0 border-t border-[#2d3345] bg-[#0f1117] p-3 text-center text-[10px] text-[#94a3b8]">
          <span className="flex items-center justify-center gap-1">
            <Sparkles className="h-3 w-3 text-indigo-400" />
            <span>FastAPI Catalog • Live In-Memory SQLite</span>
          </span>
        </div>
      </aside>
    </>
  );
};

