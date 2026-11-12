"use client";

import React from "react";
import { ShoppingBag, Bot, Sparkles, Activity, ShieldCheck, ExternalLink } from "lucide-react";

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
    <header className="sticky top-0 z-30 w-full border-b border-[#2d3345] bg-[#0f1117]/90 backdrop-blur-md transition-all">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand & Badge */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 shadow-lg shadow-indigo-500/20">
            <ShoppingBag className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight text-white">
                Cart<span className="text-indigo-400">Mind</span>
              </span>
              <span className="hidden rounded-full border border-indigo-500/30 bg-indigo-500/10 px-2 py-0.5 text-[10px] font-medium tracking-wider text-indigo-300 uppercase sm:inline-block">
                AI Agent
              </span>
            </div>
            <p className="hidden text-xs text-[#94a3b8] sm:block">
              Intelligent E-Commerce Shopping & Feedback Ops
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="flex items-center gap-1 rounded-xl border border-[#2d3345] bg-[#161922] p-1 shadow-inner">
          <button
            type="button"
            onClick={() => setActiveTab("assistant")}
            className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
              activeTab === "assistant"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "text-[#94a3b8] hover:bg-[#1c202d] hover:text-[#f8fafc]"
            }`}
          >
            <Bot className="h-4 w-4" />
            <span className="hidden sm:inline">Shopping Assistant</span>
            <span className="sm:hidden">Shop</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("feedback")}
            className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
              activeTab === "feedback"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "text-[#94a3b8] hover:bg-[#1c202d] hover:text-[#f8fafc]"
            }`}
          >
            <Activity className="h-4 w-4" />
            <span className="hidden sm:inline">Feedback Triage</span>
            <span className="sm:hidden">Feedback</span>
          </button>
        </nav>

        {/* Status Indicator & Live Demo Link */}
        <div className="flex items-center gap-3">
          <div
            className={`flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium ${
              isBackendOnline
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border-rose-500/30 bg-rose-500/10 text-rose-400"
            }`}
            title={isBackendOnline ? "FastAPI Backend is operational" : "Cannot reach FastAPI backend"}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                isBackendOnline ? "animate-pulse bg-emerald-400" : "bg-rose-400"
              }`}
            />
            <span className="hidden md:inline">
              {isBackendOnline ? "Backend Online" : "Backend Offline"}
            </span>
          </div>

          <a
            href="https://cartmind-ldonwp6c2dyc9unjjfedck.streamlit.app/"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden items-center gap-1.5 rounded-lg border border-[#2d3345] bg-[#161922] px-3 py-1.5 text-xs font-medium text-[#94a3b8] transition-colors hover:border-indigo-500/50 hover:bg-[#1c202d] hover:text-white lg:flex"
            title="Open Streamlit Live Deployment"
          >
            <span>Streamlit Cloud</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      </div>
    </header>
  );
};

