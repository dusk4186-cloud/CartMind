"use client";

import React from "react";
import { AlertCircle, AlertTriangle, Info, X } from "lucide-react";

export interface ErrorBannerProps {
  message: string;
  type?: "error" | "warning" | "info";
  title?: string;
  onDismiss?: () => void;
}

export function ErrorBanner({
  message,
  type = "error",
  title,
  onDismiss,
}: ErrorBannerProps) {
  if (!message) return null;

  const styles = {
    error: {
      bg: "bg-rose-950/40 border-rose-800/60 text-rose-200",
      icon: <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" aria-hidden="true" />,
      btn: "text-rose-400 hover:text-rose-200 focus-visible:ring-rose-400",
    },
    warning: {
      bg: "bg-amber-950/40 border-amber-800/60 text-amber-200",
      icon: <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" aria-hidden="true" />,
      btn: "text-amber-400 hover:text-amber-200 focus-visible:ring-amber-400",
    },
    info: {
      bg: "bg-indigo-950/40 border-indigo-800/60 text-indigo-200",
      icon: <Info className="w-5 h-5 text-indigo-400 shrink-0" aria-hidden="true" />,
      btn: "text-indigo-400 hover:text-indigo-200 focus-visible:ring-indigo-400",
    },
  }[type];

  return (
    <div
      role="alert"
      className={`error-banner flex items-center justify-between p-3.5 mb-4 rounded-xl border text-sm animate-in fade-in duration-200 ${styles.bg}`}
    >
      <div className="flex items-start gap-3">
        {styles.icon}
        <div className="flex flex-col">
          {title && <span className="font-semibold text-xs uppercase tracking-wider mb-0.5">{title}</span>}
          <span className="leading-snug">{message}</span>
        </div>
      </div>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className={`p-1 rounded transition-colors focus-visible:outline-none focus-visible:ring-2 ${styles.btn}`}
          aria-label="Dismiss banner"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
