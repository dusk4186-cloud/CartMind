"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import { ChatArea } from "../components/ChatArea";
import { SentimentTab } from "../components/SentimentTab";
import { ErrorBanner } from "../components/ErrorBanner";
import { Product, ChatMessage } from "../lib/types";
import { checkHealth, getProducts, sendChatMessage } from "../lib/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"assistant" | "feedback">("assistant");
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState<boolean>(true);
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);
  const [generalError, setGeneralError] = useState<string | null>(null);

  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isChatLoading, setIsChatLoading] = useState<boolean>(false);
  const [initialPrompt, setInitialPrompt] = useState<string | undefined>(undefined);

  // Check health and fetch products on mount
  const initialize = useCallback(async () => {
    setIsLoadingProducts(true);
    try {
      const isOnline = await checkHealth();
      setIsBackendOnline(isOnline);

      if (isOnline) {
        const prodData = await getProducts();
        setProducts(prodData.products || []);
        setGeneralError(null);
      } else {
        setGeneralError(
          "FastAPI backend is offline. Ensure the backend server is running on http://127.0.0.1:8000."
        );
      }
    } catch {
      setIsBackendOnline(false);
      setGeneralError(
        "Could not connect to FastAPI server. Please check your network or server status."
      );
    } finally {
      setIsLoadingProducts(false);
    }
  }, []);

  useEffect(() => {
    initialize();
  }, [initialize]);

  // Handle chat message submit
  const handleSendMessage = async (userPrompt: string) => {
    if (!userPrompt.trim()) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: userPrompt,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    // Append user message immediately
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setIsChatLoading(true);
    setGeneralError(null);

    // Prepare previous history for the API (excluding the current prompt)
    const historyPayload = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const response = await sendChatMessage(userPrompt, historyPayload);

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.reply,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        blockedBySecurity: response.blocked_by_security,
      };

      setMessages([...updatedMessages, assistantMessage]);
    } catch (err: unknown) {
      const errMsg =
        err instanceof Error
          ? err.message
          : "Failed to communicate with shopping agent.";

      const fallbackAssistantMessage: ChatMessage = {
        id: `assistant-err-${Date.now()}`,
        role: "assistant",
        content: `⚠️ **Error communicating with CartMind backend:**\n\n${errMsg}\n\nPlease verify that the FastAPI backend is online.`,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages([...updatedMessages, fallbackAssistantMessage]);
    } finally {
      setIsChatLoading(false);
    }
  };

  // Clear chat
  const handleClearChat = () => {
    setMessages([]);
  };

  // Handle clicking "Ask about this" from product sidebar
  const handleSelectProductQuery = (query: string) => {
    if (activeTab !== "assistant") {
      setActiveTab("assistant");
    }
    setInitialPrompt(query);
    setIsMobileSidebarOpen(false);
  };

  return (
    <div className="flex h-[100dvh] w-screen flex-col overflow-hidden bg-[#0f1117] text-[#f8fafc]">
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isBackendOnline={isBackendOnline}
      />

      {/* General Error Banner */}
      {generalError && (
        <div className="px-4 py-2 sm:px-6">
          <ErrorBanner
            type="warning"
            title="Connection Notice"
            message={generalError}
            onDismiss={() => setGeneralError(null)}
          />
        </div>
      )}

      {/* Main Content Area */}
      <div className="relative flex flex-1 min-h-0 overflow-hidden">
        {activeTab === "assistant" ? (
          <>
            {/* Left Sidebar (Catalogue) */}
            <Sidebar
              products={products}
              isLoading={isLoadingProducts}
              onSelectProductQuery={handleSelectProductQuery}
              isOpenMobile={isMobileSidebarOpen}
              onCloseMobile={() => setIsMobileSidebarOpen(false)}
            />

            {/* Right Chat Area */}
            <ChatArea
              messages={messages}
              isLoading={isChatLoading}
              onSendMessage={handleSendMessage}
              onClearChat={handleClearChat}
              onOpenMobileSidebar={() => setIsMobileSidebarOpen(true)}
              initialPrompt={initialPrompt}
              onClearInitialPrompt={() => setInitialPrompt(undefined)}
            />
          </>
        ) : (
          /* Customer Feedback Triage Tab */
          <SentimentTab />
        )}
      </div>
    </div>
  );
}
