"use client";

import React, { useState } from "react";
import {
  Activity,
  Sparkles,
  Lightbulb,
  CheckCircle2,
  AlertTriangle,
  Copy,
  Check,
  RefreshCw,
  Layers,
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
        <span className="inline-flex items-center gap-1 rounded-md border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-xs font-medium text-emerald-400">
          <CheckCircle2 className="h-3 w-3" />
          <span>Positive</span>
        </span>
      );
    }
    if (s.includes("neg")) {
      return (
        <span className="inline-flex items-center gap-1 rounded-md border border-rose-500/20 bg-rose-500/10 px-2 py-0.5 text-xs font-medium text-rose-400">
          <AlertTriangle className="h-3 w-3" />
          <span>Negative</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 rounded-md border border-amber-500/20 bg-amber-500/10 px-2 py-0.5 text-xs font-medium text-amber-400">
        <span>Neutral</span>
      </span>
    );
  };

  const renderPriorityBadge = (priority: string) => {
    const p = priority?.toUpperCase() || "NONE";
    if (p === "HIGH" || p === "URGENT") {
      return (
        <span className="rounded-md border border-rose-500/20 bg-rose-500/10 px-2 py-0.5 text-[10px] font-medium text-rose-300">
          HIGH PRIORITY
        </span>
      );
    }
    if (p === "MEDIUM") {
      return (
        <span className="rounded-md border border-amber-500/20 bg-amber-500/10 px-2 py-0.5 text-[10px] font-medium text-amber-300">
          MEDIUM PRIORITY
        </span>
      );
    }
    return (
      <span className="rounded-md border border-zinc-800 bg-zinc-800/60 px-2 py-0.5 text-[10px] font-medium text-zinc-400">
        STANDARD
      </span>
    );
  };

  return (
    <div className="flex-1 overflow-y-auto bg-[#09090b] p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-4xl space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-2 border-b border-[#27272a] pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-zinc-300" />
              <h1 className="text-xl font-semibold tracking-tight text-white">
                Customer Feedback Triage
              </h1>
            </div>
            <p className="mt-1 text-xs text-zinc-400">
              Automated 3-task pipeline: Sentiment Analysis, Auto-Reply Generation, and Ticket Routing.
            </p>
          </div>

          <button
            type="button"
            onClick={handleRunBatch}
            disabled={isBatchRunning}
            className="inline-flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-900 px-3.5 py-1.5 text-xs font-medium text-zinc-200 shadow-sm transition-all hover:bg-zinc-800 hover:text-white disabled:opacity-50"
          >
            <RefreshCw
              className={`h-3.5 w-3.5 ${isBatchRunning ? "animate-spin" : ""}`}
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
        <div className="rounded-xl border border-zinc-800 bg-[#121215] p-5 shadow-sm sm:p-6">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <span className="text-xs font-medium tracking-wider text-zinc-400 uppercase">
              Select Input Source
            </span>

            {/* Input Mode Selector */}
            <div className="inline-flex rounded-lg border border-zinc-800 bg-[#09090b] p-1">
              <button
                type="button"
                onClick={() => setInputMode("preset")}
                className={`rounded-md px-3 py-1 text-xs font-medium transition-all ${
                  inputMode === "preset"
                    ? "bg-zinc-800 text-white shadow-sm"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                Preset Scenario
              </button>
              <button
                type="button"
                onClick={() => setInputMode("custom")}
                className={`rounded-md px-3 py-1 text-xs font-medium transition-all ${
                  inputMode === "custom"
                    ? "bg-zinc-800 text-white shadow-sm"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                Custom Review
              </button>
            </div>
          </div>

          {/* Conditional Input UI */}
          {inputMode === "preset" ? (
            <div className="space-y-3">
              <label className="text-xs font-medium text-zinc-300">
                Choose a pre-configured scenario:
              </label>
              <select
                value={selectedPresetIndex}
                onChange={(e) => setSelectedPresetIndex(Number(e.target.value))}
                className="w-full rounded-lg border border-zinc-800 bg-[#09090b] px-3.5 py-2.5 text-xs text-zinc-100 transition-colors focus:border-zinc-500 focus:outline-none"
              >
                {PRESET_SCENARIOS.map((preset, index) => (
                  <option key={index} value={index}>
                    {preset.label} — &ldquo;{preset.text}&rdquo;
                  </option>
                ))}
              </select>
              <p className="rounded-lg border border-zinc-800/80 bg-[#16161a] px-3 py-2 text-xs italic text-zinc-300">
                &ldquo;{PRESET_SCENARIOS[selectedPresetIndex].text}&rdquo;
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <label className="text-xs font-medium text-zinc-300">
                Type customer review or feedback:
              </label>
              <textarea
                rows={3}
                value={customText}
                onChange={(e) => setCustomText(e.target.value)}
                placeholder="Enter raw customer review text..."
                className="w-full rounded-lg border border-zinc-800 bg-[#09090b] p-3 text-xs text-zinc-100 placeholder-zinc-500 transition-colors focus:border-zinc-500 focus:outline-none"
              />
            </div>
          )}

          {/* Submit Button */}
          <div className="mt-5 flex justify-end">
            <button
              type="button"
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-xs font-semibold text-zinc-950 shadow-sm transition-all hover:bg-zinc-200 disabled:opacity-50"
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                  <span>Analyzing Pipeline...</span>
                </>
              ) : (
                <>
                  <Zap className="h-3.5 w-3.5" />
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
              <Sparkles className="h-4 w-4 text-zinc-300" />
              <h2 className="text-sm font-semibold text-white">
                Analysis & Routing Results
              </h2>
            </div>

            {/* 3 Result Cards Grid */}
            <div className="grid grid-cols-1 gap-3.5 md:grid-cols-3">
              {/* Card 1: Sentiment & Category */}
              <div className="flex flex-col justify-between rounded-xl border border-zinc-800 bg-[#121215] p-4">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-semibold tracking-wider text-zinc-400 uppercase">
                      Sentiment & Category
                    </span>
                    {renderSentimentBadge(singleResult.sentiment.sentiment)}
                  </div>

                  <div className="mt-3.5 space-y-2.5">
                    <div>
                      <span className="text-[10px] tracking-wider text-zinc-500 uppercase">
                        Intent
                      </span>
                      <p className="text-xs font-semibold text-zinc-200">
                        {singleResult.sentiment.categorization || "N/A"}
                      </p>
                    </div>

                    <div>
                      <span className="text-[10px] tracking-wider text-zinc-500 uppercase">
                        Feedback Area
                      </span>
                      <p className="text-xs font-semibold text-zinc-200">
                        {singleResult.sentiment.feedback_area || "General"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Card 2: Suggested Response */}
              <div className="flex flex-col justify-between rounded-xl border border-zinc-800 bg-[#121215] p-4">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-semibold tracking-wider text-zinc-400 uppercase">
                      Generated Auto-Reply
                    </span>
                    <button
                      type="button"
                      onClick={() => copyResponse(singleResult.suggested_response)}
                      className="flex items-center gap-1 rounded border border-zinc-800 bg-zinc-900 px-2 py-0.5 text-[10px] text-zinc-400 hover:text-white"
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

                  <div className="mt-3 rounded-lg border border-zinc-800/80 bg-[#09090b] p-3">
                    <p className="text-xs leading-relaxed text-zinc-300 italic">
                      &ldquo;{singleResult.suggested_response}&rdquo;
                    </p>
                  </div>
                </div>
              </div>

              {/* Card 3: Support Action & Routing */}
              <div className="flex flex-col justify-between rounded-xl border border-zinc-800 bg-[#121215] p-4">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-semibold tracking-wider text-zinc-400 uppercase">
                      Support Action & Routing
                    </span>
                    {renderPriorityBadge(singleResult.routing.priority)}
                  </div>

                  <div className="mt-3.5 space-y-2.5">
                    <div>
                      <span className="text-[10px] tracking-wider text-zinc-500 uppercase">
                        Routing Target
                      </span>
                      <div className="mt-1">
                        <span className="inline-block rounded border border-zinc-700 bg-zinc-800/80 px-2 py-0.5 text-xs font-medium text-zinc-200">
                          {singleResult.routing.routing_target || "N/A"}
                        </span>
                      </div>
                    </div>

                    <div>
                      <span className="text-[10px] tracking-wider text-zinc-500 uppercase">
                        Action
                      </span>
                      <p className="text-xs font-medium text-zinc-300">
                        {singleResult.routing.routing_action || "Standard resolution"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Exactly ONE Diagnostic Commentary Box */}
            {singleResult.sentiment.commentary && (
              <div className="flex items-start gap-2.5 rounded-lg border border-zinc-700/80 bg-zinc-900/60 p-3.5 text-xs text-zinc-300">
                <Lightbulb className="h-4 w-4 shrink-0 text-amber-400" />
                <div>
                  <span className="font-semibold text-zinc-200">
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
          <div className="space-y-4 pt-4">
            <div className="flex items-center justify-between border-t border-[#27272a] pt-4">
              <div className="flex items-center gap-2">
                <Layers className="h-4 w-4 text-zinc-300" />
                <h2 className="text-sm font-semibold text-white">
                  Batch Evaluation Results
                </h2>
              </div>
              {batchResult && (
                <span className="text-xs text-zinc-400">
                  Processed {batchResult.total_processed} items in{" "}
                  {batchResult.processing_time_ms}ms
                </span>
              )}
            </div>

            {isBatchRunning ? (
              <div className="flex flex-col items-center justify-center rounded-xl border border-zinc-800 bg-[#121215] p-10 text-center">
                <RefreshCw className="h-6 w-6 animate-spin text-zinc-300" />
                <p className="mt-2 text-xs font-semibold text-white">
                  Running Concurrent LangGraph Triage Pipeline...
                </p>
              </div>
            ) : batchResult ? (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {batchResult.results.map((item: BatchItemResult, idx: number) => (
                  <div
                    key={idx}
                    className="flex flex-col justify-between rounded-xl border border-zinc-800 bg-[#121215] p-4 text-xs transition-all hover:border-zinc-700"
                  >
                    <div>
                      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
                        <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">
                          Review {String(idx + 1).padStart(2, "0")}
                        </span>
                        {renderSentimentBadge(item.task1.sentiment.value)}
                      </div>

                      <p className="mt-2.5 font-medium text-zinc-100">
                        &ldquo;{item.review}&rdquo;
                      </p>

                      <div className="mt-2.5 flex items-center gap-2 text-[10px]">
                        <span className="rounded bg-[#09090b] px-2 py-0.5 text-zinc-300">
                          {item.task1.categorization.value}
                        </span>
                        <span className="rounded bg-[#09090b] px-2 py-0.5 text-zinc-400">
                          {item.task1.feedback_area.value}
                        </span>
                      </div>

                      <div className="mt-2.5 rounded-lg border border-zinc-800/80 bg-[#09090b] p-2.5">
                        <span className="text-[10px] font-semibold text-zinc-400 uppercase">
                          Suggested Response:
                        </span>
                        <p className="mt-1 text-[11px] text-zinc-300 italic">
                          &ldquo;{item.task2.auto_reply_message}&rdquo;
                        </p>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center justify-between border-t border-zinc-800 pt-2 text-[10px]">
                      <span className="text-zinc-500">Routing:</span>
                      <span className="font-semibold text-zinc-200">
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
