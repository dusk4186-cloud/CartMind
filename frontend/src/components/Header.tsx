"use client";

import React from "react";
import { ShoppingBag, Bot, Activity, ExternalLink } from "lucide-react";

interface HeaderProps {
  activeTab: "assistant" | "feedback";
  setActiveTab: (tab: "assistant" | "feedback") => void;
  isBackendOnline: boolean;
  onResetSession?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  isBackendOnline,
}) => {
  return (
    <header className="sticky top-0 z-30 shrink-0 w-full border-b border-[#27272a] bg-[#09090b]/95 backdrop-blur-md transition-all">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-700/70 bg-zinc-900 shadow-sm">
            <ShoppingBag className="h-4 w-4 text-zinc-100" />
          </div>
          <div className="flex flex-col">
            <span className="text-base font-semibold tracking-tight text-white">
              CartMind
            </span>
            <p className="hidden text-xs text-zinc-400 sm:block">
              Intelligent E-Commerce Shopping & Feedback Ops
            </p>
          </div>
        </div>

        {/* Tab Navigation (Linear Segmented Control) */}
        <nav className="flex items-center gap-1 rounded-lg border border-zinc-800 bg-zinc-900/90 p-1">
          <button
            type="button"
            onClick={() => setActiveTab("assistant")}
            className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition-all ${
              activeTab === "assistant"
                ? "bg-zinc-800 text-white shadow-sm"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Bot className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Shopping Assistant</span>
            <span className="sm:hidden">Shop</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("feedback")}
            className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition-all ${
              activeTab === "feedback"
                ? "bg-zinc-800 text-white shadow-sm"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Activity className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Feedback Triage</span>
            <span className="sm:hidden">Feedback</span>
          </button>
        </nav>

        {/* Status Indicator & Live Demo Link */}
        <div className="flex items-center gap-2.5">
          <div
            className={`flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs font-medium ${
              isBackendOnline
                ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
                : "border-rose-500/20 bg-rose-500/10 text-rose-400"
            }`}
            title={isBackendOnline ? "FastAPI Backend is operational" : "Cannot reach FastAPI backend"}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                isBackendOnline ? "bg-emerald-400" : "bg-rose-400"
              }`}
            />
            <span className="hidden md:inline">
              {isBackendOnline ? "Online" : "Offline"}
            </span>
          </div>

          <a
            href="https://cartmind-ldonwp6c2dyc9unjjfedck.streamlit.app/"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden items-center gap-1.5 rounded-md border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-xs font-medium text-zinc-400 transition-colors hover:border-zinc-700 hover:text-zinc-100 lg:flex"
            title="Open Streamlit Live Deployment"
          >
            <span>Streamlit Cloud</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      </div>
    </header>
  );
};
