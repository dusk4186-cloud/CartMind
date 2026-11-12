"use client";

import React, { useState } from "react";
import {
  Activity,
  Sparkles,
  Send,
  Lightbulb,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Copy,
  Check,
  RefreshCw,
  Layers,
  ShieldCheck,
  Zap,
} from "lucide-react";
import {
  SentimentAnalysisResult,
  BatchAnalysisResult,
  BatchItemResult,
} from "../lib/types";
import { analyzeFeedback, analyzeFeedbackBatch } from "../lib/api";
import { ErrorBanner } from "./ErrorBanner";

const PRESET_SCENARIOS = [
  {
    label: "Positive Statement — Hiking Shoes",
    text: "Great shoes, if you love trekking",
  },
  {
    label: "Sarcastic Complaint — Stiff Leather Belt",
    text: "This belt is so good, feeling like ants biting my waist",
  },
  {
    label: "Damaged Delivery — Leather Jacket",
    text: "The jacket arrived damaged, please replace it.",
  },
  {
    label: "Order Delay Inquiry — Logistics",
    text: "My order was delayed by two weeks, what happened?",
  },
  {
    label: "Defect Complaint — Stitching Problem",
    text: "The stitching on this wallet came undone after just two days.",
  },
];

export const SentimentTab: React.FC = () => {
  // Input mode: preset vs custom
  const [inputMode, setInputMode] = useState<"preset" | "custom">("preset");
  const [selectedPresetIndex, setSelectedPresetIndex] = useState<number>(0);
  const [customText, setCustomText] = useState<string>("");

  // Single analysis state
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [singleResult, setSingleResult] =
    useState<SentimentAnalysisResult | null>(null);
  const [copiedReply, setCopiedReply] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Batch analysis state
  const [isBatchRunning, setIsBatchRunning] = useState<boolean>(false);
  const [batchResult, setBatchResult] = useState<BatchAnalysisResult | null>(
    null
  );
  const [showBatchSection, setShowBatchSection] = useState<boolean>(false);

  // Run single analysis
  const handleAnalyze = async () => {
    const textToAnalyze =
      inputMode === "preset"
        ? PRESET_SCENARIOS[selectedPresetIndex].text
        : customText.trim();

    if (!textToAnalyze) {
      setErrorMessage("Please enter a customer review to analyze.");
      return;
    }

    setErrorMessage(null);
    setIsAnalyzing(true);

    try {
      const result = await analyzeFeedback(textToAnalyze);
      setSingleResult(result);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to analyze review";
      setErrorMessage(message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Run batch analysis
  const handleRunBatch = async () => {
    setShowBatchSection(true);
    setIsBatchRunning(true);
    setErrorMessage(null);

    const reviews = [
      "Absolutely love this brand! The wallet I bought is stylish and durable.",
      "The leather jacket fits perfectly and feels premium.",
      "The jacket arrived damaged, please replace it.",
      "My order was delayed by two weeks, what happened?",
    ];

    try {
      const data = await analyzeFeedbackBatch(reviews);
      setBatchResult(data);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to run batch analysis";
      setErrorMessage(message);
    } finally {
      setIsBatchRunning(false);
    }
  };

  const copyResponse = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedReply(true);
    setTimeout(() => setCopiedReply(false), 2000);
  };

  const renderSentimentBadge = (sentiment: string) => {
    const s = sentiment?.toLowerCase() || "";
    if (s.includes("pos")) {
      return (
        <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-400 uppercase">
          <CheckCircle2 className="h-3 w-3" />
          <span>Positive</span>
        </span>
      );
    }
    if (s.includes("neg")) {
      return (
        <span className="inline-flex items-center gap-1 rounded-full border border-rose-500/30 bg-rose-500/10 px-2.5 py-0.5 text-xs font-semibold text-rose-400 uppercase">
          <AlertTriangle className="h-3 w-3" />
          <span>Negative</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-0.5 text-xs font-semibold text-amber-400 uppercase">
        <span>Neutral</span>
      </span>
    );
  };

  const renderPriorityBadge = (priority: string) => {
    const p = priority?.toUpperCase() || "NONE";
    if (p === "HIGH" || p === "URGENT") {
      return (
        <span className="rounded-full bg-rose-500/20 px-2 py-0.5 text-[10px] font-bold text-rose-300">
          HIGH PRIORITY
        </span>
      );
    }
    if (p === "MEDIUM") {
      return (
        <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-300">
          MEDIUM PRIORITY
        </span>
      );
    }
    return (
      <span className="rounded-full bg-slate-700/50 px-2 py-0.5 text-[10px] font-medium text-slate-400">
        STANDARD
      </span>
    );
  };

  return (
    <div className="flex-1 overflow-y-auto bg-[#0f1117] p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-5xl space-y-8">
        {/* Header */}
        <div className="flex flex-col gap-2 border-b border-[#2d3345] pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Activity className="h-6 w-6 text-indigo-400" />
              <h1 className="text-2xl font-bold tracking-tight text-white">
                Customer Feedback Triage
              </h1>
            </div>
            <p className="mt-1 text-sm text-[#94a3b8]">
              Automated 3-task pipeline: Sentiment Analysis, Auto-Reply
              Generation, and Ticket Routing.
            </p>
          </div>

          <button
            type="button"
            onClick={handleRunBatch}
            disabled={isBatchRunning}
            className="inline-flex items-center gap-2 rounded-xl border border-indigo-500/30 bg-[#161922] px-4 py-2 text-xs font-semibold text-indigo-300 shadow-md transition-all hover:border-indigo-500 hover:bg-indigo-600 hover:text-white disabled:opacity-50"
          >
            <RefreshCw
              className={`h-4 w-4 ${isBatchRunning ? "animate-spin" : ""}`}
            />
            <span>{isBatchRunning ? "Running Batch..." : "Batch Evaluation"}</span>
          </button>
        </div>

        {errorMessage && (
          <ErrorBanner
            type="error"
            title="Analysis Error"
            message={errorMessage}
            onDismiss={() => setErrorMessage(null)}
          />
        )}

        {/* Input Card */}
        <div className="rounded-2xl border border-[#2d3345] bg-[#161922] p-5 shadow-lg sm:p-6">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <span className="text-xs font-semibold tracking-wider text-[#94a3b8] uppercase">
              Select Input Source
            </span>

            {/* Input Mode Selector */}
            <div className="inline-flex rounded-xl border border-[#2d3345] bg-[#0f1117] p-1">
              <button
                type="button"
                onClick={() => setInputMode("preset")}
                className={`rounded-lg px-3 py-1 text-xs font-medium transition-all ${
                  inputMode === "preset"
                    ? "bg-indigo-600 text-white shadow"
                    : "text-[#94a3b8] hover:text-white"
                }`}
              >
                Preset Scenario
              </button>
              <button
                type="button"
                onClick={() => setInputMode("custom")}
                className={`rounded-lg px-3 py-1 text-xs font-medium transition-all ${
                  inputMode === "custom"
                    ? "bg-indigo-600 text-white shadow"
                    : "text-[#94a3b8] hover:text-white"
                }`}
              >
                Custom Review
              </button>
            </div>
          </div>

          {/* Conditional Input UI */}
          {inputMode === "preset" ? (
            <div className="space-y-3">
              <label className="text-xs font-medium text-slate-300">
                Choose a pre-configured scenario:
              </label>
              <select
                value={selectedPresetIndex}
                onChange={(e) => setSelectedPresetIndex(Number(e.target.value))}
                className="w-full rounded-xl border border-[#2d3345] bg-[#0f1117] px-4 py-3 text-sm text-[#f8fafc] transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                {PRESET_SCENARIOS.map((preset, index) => (
                  <option key={index} value={index}>
                    {preset.label} — &ldquo;{preset.text}&rdquo;
                  </option>
                ))}
              </select>
              <p className="rounded-lg bg-[#1c202d] px-3 py-2 text-xs italic text-[#cbd5e1]">
                &ldquo;{PRESET_SCENARIOS[selectedPresetIndex].text}&rdquo;
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <label className="text-xs font-medium text-slate-300">
                Type customer review or feedback:
              </label>
              <textarea
                rows={3}
                value={customText}
                onChange={(e) => setCustomText(e.target.value)}
                placeholder="Enter raw customer review text..."
                className="w-full rounded-xl border border-[#2d3345] bg-[#0f1117] p-3 text-sm text-[#f8fafc] placeholder-[#94a3b8] transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          )}

          {/* Submit Button */}
          <div className="mt-5 flex justify-end">
            <button
              type="button"
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition-all hover:from-indigo-500 hover:to-indigo-400 disabled:opacity-50"
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Analyzing Pipeline...</span>
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4" />
                  <span>Analyze Review</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Single Analysis Results Display */}
        {singleResult && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-400" />
              <h2 className="text-lg font-bold text-white">
                Analysis & Routing Results
              </h2>
            </div>

            {/* 3 Result Cards Grid */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {/* Card 1: Sentiment & Category */}
              <div className="flex flex-col justify-between rounded-2xl border border-[#2d3345] bg-[#161922] p-5">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold tracking-wider text-[#94a3b8] uppercase">
                      Sentiment & Category
                    </span>
                    {renderSentimentBadge(singleResult.sentiment.sentiment)}
                  </div>

                  <div className="mt-4 space-y-3">
                    <div>
                      <span className="text-[10px] tracking-wider text-[#94a3b8] uppercase">
                        Intent
                      </span>
                      <p className="text-sm font-semibold text-[#f8fafc]">
                        {singleResult.sentiment.categorization || "N/A"}
                      </p>
                    </div>

                    <div>
                      <span className="text-[10px] tracking-wider text-[#94a3b8] uppercase">
                        Feedback Area
                      </span>
                      <p className="text-sm font-semibold text-[#f8fafc]">
                        {singleResult.sentiment.feedback_area || "General"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Card 2: Suggested Response */}
              <div className="flex flex-col justify-between rounded-2xl border border-[#2d3345] bg-[#161922] p-5">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold tracking-wider text-[#94a3b8] uppercase">
                      Generated Auto-Reply
                    </span>
                    <button
                      type="button"
                      onClick={() => copyResponse(singleResult.suggested_response)}
                      className="flex items-center gap-1 rounded-md bg-[#1c202d] px-2 py-0.5 text-[10px] text-[#94a3b8] hover:text-white"
                      title="Copy response"
                    >
                      {copiedReply ? (
                        <>
                          <Check className="h-3 w-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-3 w-3" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>

                  <div className="mt-3 rounded-xl bg-[#0f1117] p-3">
                    <p className="text-xs leading-relaxed text-[#cbd5e1] italic">
                      &ldquo;{singleResult.suggested_response}&rdquo;
                    </p>
                  </div>
                </div>
              </div>

              {/* Card 3: Support Action & Routing */}
              <div className="flex flex-col justify-between rounded-2xl border border-[#2d3345] bg-[#161922] p-5">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold tracking-wider text-[#94a3b8] uppercase">
                      Support Action & Routing
                    </span>
                    {renderPriorityBadge(singleResult.routing.priority)}
                  </div>

                  <div className="mt-4 space-y-3">
                    <div>
                      <span className="text-[10px] tracking-wider text-[#94a3b8] uppercase">
                        Routing Target
                      </span>
                      <div className="mt-1">
                        <span className="inline-block rounded-md bg-indigo-500/10 px-2.5 py-1 text-xs font-semibold text-indigo-300">
                          {singleResult.routing.routing_target || "N/A"}
                        </span>
                      </div>
                    </div>

                    <div>
                      <span className="text-[10px] tracking-wider text-[#94a3b8] uppercase">
                        Action
                      </span>
                      <p className="text-xs font-medium text-slate-300">
                        {singleResult.routing.routing_action || "Standard resolution"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* FIXED: Exactly ONE Diagnostic Commentary Box */}
            {singleResult.sentiment.commentary && (
              <div className="flex items-start gap-3 rounded-xl border border-sky-500/30 bg-sky-950/20 p-4 text-xs text-sky-200">
                <Lightbulb className="h-5 w-5 shrink-0 text-sky-400" />
                <div>
                  <span className="font-semibold text-sky-300">
                    Diagnostic Commentary:{" "}
                  </span>
                  <span>{singleResult.sentiment.commentary}</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Batch Evaluation Results Section */}
        {showBatchSection && (
          <div className="space-y-4 pt-6">
            <div className="flex items-center justify-between border-t border-[#2d3345] pt-6">
              <div className="flex items-center gap-2">
                <Layers className="h-5 w-5 text-indigo-400" />
                <h2 className="text-lg font-bold text-white">
                  Batch Evaluation Results
                </h2>
              </div>
              {batchResult && (
                <span className="text-xs text-[#94a3b8]">
                  Processed {batchResult.total_processed} items in{" "}
                  {batchResult.processing_time_ms}ms
                </span>
              )}
            </div>

            {isBatchRunning ? (
              <div className="flex flex-col items-center justify-center rounded-2xl border border-[#2d3345] bg-[#161922] p-12 text-center">
                <RefreshCw className="h-8 w-8 animate-spin text-indigo-400" />
                <p className="mt-3 text-sm font-semibold text-white">
                  Running Concurrent LangGraph Triage Pipeline...
                </p>
                <p className="mt-1 text-xs text-[#94a3b8]">
                  Classifying sentiment, drafting replies, and routing tickets.
                </p>
              </div>
            ) : batchResult ? (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {batchResult.results.map((item: BatchItemResult, idx: number) => (
                  <div
                    key={idx}
                    className="flex flex-col justify-between rounded-2xl border border-[#2d3345] bg-[#161922] p-4 text-xs transition-all hover:border-indigo-500/50"
                  >
                    <div>
                      <div className="flex items-center justify-between pb-2 border-b border-[#2d3345]">
                        <span className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">
                          Review {String(idx + 1).padStart(2, "0")}
                        </span>
                        {renderSentimentBadge(item.task1.sentiment.value)}
                      </div>

                      <p className="mt-3 font-medium text-[#f8fafc]">
                        &ldquo;{item.review}&rdquo;
                      </p>

                      <div className="mt-3 flex items-center gap-2 text-[10px]">
                        <span className="rounded bg-[#0f1117] px-2 py-0.5 text-indigo-300">
                          {item.task1.categorization.value}
                        </span>
                        <span className="rounded bg-[#0f1117] px-2 py-0.5 text-slate-400">
                          {item.task1.feedback_area.value}
                        </span>
                      </div>

                      <div className="mt-3 rounded-lg bg-[#0f1117] p-2.5">
                        <span className="text-[10px] font-semibold text-[#94a3b8] uppercase">
                          Suggested Response:
                        </span>
                        <p className="mt-1 text-[11px] text-[#cbd5e1] italic">
                          &ldquo;{item.task2.auto_reply_message}&rdquo;
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center justify-between border-t border-[#2d3345] pt-2 text-[10px]">
                      <span className="text-[#94a3b8]">Routing:</span>
                      <span className="font-semibold text-amber-400">
                        {item.task3.routing_action}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
};

