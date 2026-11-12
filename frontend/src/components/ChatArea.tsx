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
    <div className="relative flex flex-1 flex-col overflow-hidden bg-[#0f1117]">
      {/* Top action bar */}
      <div className="flex h-12 items-center justify-between border-b border-[#2d3345] bg-[#161922]/50 px-4">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onOpenMobileSidebar}
            className="flex items-center gap-1.5 rounded-lg border border-[#2d3345] bg-[#1c202d] px-2.5 py-1 text-xs font-medium text-[#94a3b8] hover:border-indigo-500/50 hover:text-white lg:hidden"
          >
            <PanelLeft className="h-4 w-4" />
            <span>Catalogue</span>
          </button>
          <div className="hidden items-center gap-2 text-xs text-[#94a3b8] sm:flex">
            <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
            <span>Agent: ReAct with Gemini 2.5 Flash</span>
          </div>
        </div>

        {messages.length > 0 && (
          <button
            type="button"
            onClick={onClearChat}
            disabled={isLoading}
            className="flex items-center gap-1 rounded-lg border border-[#2d3345] bg-[#1c202d] px-2.5 py-1 text-xs font-medium text-[#94a3b8] transition-colors hover:border-rose-500/40 hover:bg-rose-500/10 hover:text-rose-400 disabled:opacity-50"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-4xl space-y-6">
          {messages.length === 0 ? (
            /* Empty State / Hero */
            <div className="flex flex-col items-center justify-center pt-8 pb-12 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-400 shadow-xl shadow-indigo-500/20">
                <Bot className="h-8 w-8 text-white" />
              </div>
              <h1 className="mt-4 text-2xl font-bold tracking-tight text-white sm:text-3xl">
                Smart Shopping Assistant
              </h1>
              <p className="mt-2 max-w-lg text-sm text-[#94a3b8]">
                Ask me anything about product availability, specs, price
                comparisons, or discounts across our store catalogue.
              </p>

              {/* Sample Prompts */}
              <div className="mt-8 w-full max-w-2xl">
                <p className="text-left text-xs font-semibold tracking-wider text-[#94a3b8] uppercase">
                  Quick Sample Prompts
                </p>
                <div className="mt-3 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                  {SAMPLE_PROMPTS.map((prompt, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => onSendMessage(prompt)}
                      className="flex items-start gap-2.5 rounded-xl border border-[#2d3345] bg-[#161922] p-3 text-left text-xs text-[#cbd5e1] transition-all hover:border-indigo-500/50 hover:bg-[#1c202d] hover:text-white hover:shadow-md"
                    >
                      <Sparkles className="mt-0.5 h-3.5 w-3.5 shrink-0 text-indigo-400" />
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
                className={`flex gap-3 sm:gap-4 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "assistant" && (
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 shadow-md shadow-indigo-600/30">
                    <Bot className="h-5 w-5 text-white" />
                  </div>
                )}

                <div
                  className={`group relative max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 shadow-md sm:px-5 sm:py-4 ${
                    message.role === "user"
                      ? "bg-indigo-600 text-white"
                      : "border border-[#2d3345] bg-[#161922] text-[#f8fafc]"
                  }`}
                >
                  {/* Security blocked warning */}
                  {message.blockedBySecurity && (
                    <div className="mb-2 flex items-center gap-2 rounded-lg bg-rose-500/20 px-3 py-1.5 text-xs font-medium text-rose-300">
                      <ShieldAlert className="h-4 w-4" />
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
                    <div className="mt-3 flex items-center justify-between border-t border-[#2d3345]/50 pt-2 text-[11px] text-[#94a3b8]">
                      <span>{message.timestamp}</span>
                      <button
                        type="button"
                        onClick={() => copyToClipboard(message.content, message.id)}
                        className="flex items-center gap-1 rounded px-1.5 py-0.5 hover:bg-[#232838] hover:text-white"
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
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#232838] text-[#94a3b8]">
                    <User className="h-5 w-5" />
                  </div>
                )}
              </div>
            ))
          )}

          {/* Thinking / Loading State */}
          {isLoading && (
            <div className="flex items-start gap-3 sm:gap-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 shadow-md">
                <Bot className="h-5 w-5 text-white animate-spin" />
              </div>
              <div className="flex items-center gap-2 rounded-2xl border border-[#2d3345] bg-[#161922] px-4 py-3 text-xs text-[#94a3b8]">
                <span className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse" />
                <span className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse delay-75" />
                <span className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse delay-150" />
                <span className="ml-2 font-medium text-slate-300">
                  CartMind is reasoning and fetching catalogue data...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Sticky Bottom Input Bar */}
      <div className="border-t border-[#2d3345] bg-[#161922]/90 p-4 backdrop-blur-md">
        <form
          onSubmit={handleSubmit}
          className="mx-auto flex max-w-4xl flex-col gap-2"
        >
          <div className="relative flex items-end rounded-2xl border border-[#2d3345] bg-[#0f1117] p-2 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500">
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about products, prices, or comparisons..."
              className="max-h-32 min-h-[44px] w-full resize-none bg-transparent px-3 py-2.5 text-sm text-[#f8fafc] placeholder-[#94a3b8] focus:outline-none"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-600/30 transition-all hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed"
              title="Send Message"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>

          <div className="flex items-center justify-between px-2 text-[11px] text-[#94a3b8]">
            <span>Press Enter to send, Shift + Enter for new line</span>
            <span className="hidden sm:inline">
              Prompt Injection & Output Sanitization Active
            </span>
          </div>
        </form>
      </div>
    </div>
  );
};

