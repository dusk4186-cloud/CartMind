"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Send,
  Bot,
  User,
  Sparkles,
  Trash2,
  Copy,
  Check,
  ShieldAlert,
  PanelLeft,
} from "lucide-react";
import { ChatMessage } from "../lib/types";

interface ChatAreaProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (content: string) => void;
  onClearChat: () => void;
  onOpenMobileSidebar: () => void;
  initialPrompt?: string;
  onClearInitialPrompt?: () => void;
}

const SAMPLE_PROMPTS = [
  "Can u show me leather based wallets under INR 1500",
  "Compare formal leather belts for office wear",
  "Find running shoes with discounts above 20%",
  "Is the Woodland Hunter wallet currently in stock?",
];

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onClearChat,
  onOpenMobileSidebar,
  initialPrompt,
  onClearInitialPrompt,
}) => {
  const [input, setInput] = useState<string>("");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Sync external initialPrompt into input if passed
  useEffect(() => {
    if (initialPrompt) {
      setInput(initialPrompt);
      if (onClearInitialPrompt) onClearInitialPrompt();
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
  }, [initialPrompt, onClearInitialPrompt]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="relative flex flex-1 min-h-0 h-full flex-col overflow-hidden bg-[#09090b]">
      {/* Top Action Bar */}
      <div className="flex h-11 shrink-0 items-center justify-between border-b border-[#27272a] bg-[#121215]/80 px-4">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onOpenMobileSidebar}
            className="flex items-center gap-1.5 rounded-md border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-xs font-medium text-zinc-400 hover:border-zinc-700 hover:text-white lg:hidden"
          >
            <PanelLeft className="h-3.5 w-3.5" />
            <span>Catalogue</span>
          </button>
          <div className="hidden items-center gap-1.5 text-xs text-zinc-400 sm:flex">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            <span>ReAct Agent (Gemini Flash + Groq LPU Fallback)</span>
          </div>
        </div>

        {messages.length > 0 && (
          <button
            type="button"
            onClick={onClearChat}
            disabled={isLoading}
            className="flex items-center gap-1 rounded-md border border-zinc-800 bg-zinc-900 px-2 py-1 text-xs font-medium text-zinc-400 transition-colors hover:border-zinc-700 hover:text-zinc-200 disabled:opacity-50"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Clear Chat</span>
          </button>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-3xl space-y-5">
          {messages.length === 0 ? (
            /* Empty State / Hero with Centered Custom Prompt Field */
            <div className="flex flex-col items-center justify-center text-center py-6 sm:py-10">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-zinc-700/80 bg-zinc-900 text-zinc-100 shadow-sm">
                <Bot className="h-6 w-6" />
              </div>
              <h1 className="mt-3.5 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                Smart Shopping Assistant
              </h1>
              <p className="mt-1.5 max-w-md text-xs sm:text-sm text-zinc-400">
                Ask anything about product availability, specs, prices, or comparisons across our catalogue.
              </p>

              {/* Centered Custom Prompt Input Field */}
              <div className="mt-6 w-full max-w-xl text-left">
                <form
                  onSubmit={handleSubmit}
                  className="rounded-xl border border-zinc-700/90 bg-[#121215] p-3 shadow-xl transition-all focus-within:border-zinc-500"
                >
                  <div className="flex items-start gap-2.5">
                    <Sparkles className="mt-1 h-4 w-4 text-zinc-400 shrink-0" />
                    <textarea
                      ref={textareaRef}
                      rows={2}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Type your shopping prompt (e.g. 'Show me casual shoes under ₹2000')..."
                      className="w-full resize-none border-0 bg-transparent text-sm text-zinc-100 placeholder-zinc-500 outline-none ring-0 shadow-none focus:outline-none focus:ring-0 focus-visible:outline-none focus-visible:ring-0 whitespace-pre-wrap break-words leading-relaxed"
                      style={{ outline: "none", border: "none", boxShadow: "none" }}
                    />
                  </div>
                  <div className="mt-2 flex items-center justify-end border-t border-zinc-800 pt-2.5">
                    <button
                      type="submit"
                      disabled={!input.trim() || isLoading}
                      className="flex items-center gap-1.5 rounded-lg bg-white px-4 py-1.5 text-xs font-semibold text-zinc-950 shadow-sm transition-all hover:bg-zinc-200 disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      <span>Ask Assistant</span>
                      <Send className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </form>
              </div>

              {/* Quick Sample Prompts */}
              <div className="mt-6 w-full max-w-xl text-left">
                <p className="text-[11px] font-medium tracking-wider text-zinc-400 uppercase">
                  Or pick a sample query:
                </p>
                <div className="mt-2.5 grid grid-cols-1 gap-2 sm:grid-cols-2">
                  {SAMPLE_PROMPTS.map((prompt, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => onSendMessage(prompt)}
                      className="flex items-start gap-2 rounded-xl border border-zinc-800 bg-[#121215] p-2.5 text-left text-xs text-zinc-300 transition-all hover:border-zinc-700 hover:bg-[#18181b] hover:text-white"
                    >
                      <Sparkles className="mt-0.5 h-3.5 w-3.5 shrink-0 text-zinc-400" />
                      <span>{prompt}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Chat Messages List */
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 sm:gap-3.5 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "assistant" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-zinc-700 bg-zinc-900 text-zinc-200 shadow-sm">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`group relative max-w-[85%] sm:max-w-[75%] rounded-xl px-4 py-3 shadow-sm ${
                    message.role === "user"
                      ? "border border-zinc-700/70 bg-zinc-800 text-zinc-100"
                      : "border border-zinc-800/90 bg-[#121215] text-zinc-200"
                  }`}
                >
                  {/* Security blocked warning */}
                  {message.blockedBySecurity && (
                    <div className="mb-2 flex items-center gap-2 rounded-md bg-rose-500/10 px-3 py-1.5 text-xs font-medium text-rose-300">
                      <ShieldAlert className="h-3.5 w-3.5" />
                      <span>Query blocked by security sanitizer</span>
                    </div>
                  )}

                  {/* Message Content */}
                  <div className="markdown-content text-sm leading-relaxed">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>

                  {/* Footer actions for assistant message */}
                  {message.role === "assistant" && (
                    <div className="mt-2.5 flex items-center justify-between border-t border-zinc-800/80 pt-1.5 text-[11px] text-zinc-500">
                      <span>{message.timestamp}</span>
                      <button
                        type="button"
                        onClick={() => copyToClipboard(message.content, message.id)}
                        className="flex items-center gap-1 rounded px-1.5 py-0.5 hover:bg-zinc-800 hover:text-zinc-200"
                        title="Copy message"
                      >
                        {copiedId === message.id ? (
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
                  )}
                </div>

                {message.role === "user" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-zinc-700 bg-zinc-800 text-zinc-300">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))
          )}

          {/* Thinking / Loading State (Static Avatar + 3 Pulsing Dots) */}
          {isLoading && (
            <div className="flex items-start gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-zinc-700 bg-zinc-900 text-zinc-200 shadow-sm">
                <Bot className="h-4 w-4" />
              </div>
              <div className="flex items-center gap-2 rounded-xl border border-zinc-800 bg-[#121215] px-4 py-2.5 text-xs text-zinc-400">
                <span className="h-1.5 w-1.5 rounded-full bg-zinc-300 animate-pulse" />
                <span className="h-1.5 w-1.5 rounded-full bg-zinc-300 animate-pulse delay-75" />
                <span className="h-1.5 w-1.5 rounded-full bg-zinc-300 animate-pulse delay-150" />
                <span className="ml-1.5 font-medium text-zinc-300">
                  CartMind is querying catalogue and checking inventory...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Docked Sticky Bottom Input Bar (Active when in conversation) */}
      {messages.length > 0 && (
        <div className="shrink-0 border-t border-[#27272a] bg-[#121215] p-3 sm:p-4 z-20">
          <form
            onSubmit={handleSubmit}
            className="mx-auto flex max-w-3xl flex-col"
          >
            <div className="relative flex items-center rounded-xl border border-zinc-800 bg-[#09090b] p-1.5 transition-all focus-within:border-zinc-500">
              <textarea
                ref={textareaRef}
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask follow-up questions about products, comparisons, or prices..."
                className="max-h-32 min-h-[38px] w-full resize-none border-0 bg-transparent px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 outline-none ring-0 shadow-none focus:outline-none focus:ring-0 focus-visible:outline-none focus-visible:ring-0 whitespace-pre-wrap break-words leading-relaxed"
                style={{ outline: "none", border: "none", boxShadow: "none" }}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white text-zinc-950 shadow-sm transition-all hover:bg-zinc-200 disabled:opacity-40 disabled:cursor-not-allowed"
                title="Send Message"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
