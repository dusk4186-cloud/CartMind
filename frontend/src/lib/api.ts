import { Product, SentimentAnalysisResult, BatchAnalysisResult } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function checkBackendHealth(): Promise<{
  online: boolean;
  catalog_size?: number;
  reviews_count?: number;
  error?: string;
}> {
  try {
    const res = await fetch(`${BASE_URL}/health`, {
      method: "GET",
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return {
      online: true,
      catalog_size: data.catalog_size,
      reviews_count: data.reviews_count,
    };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return { online: false, error: message };
  }
}

export async function fetchProducts(category?: string): Promise<Product[]> {
  try {
    const url = new URL(`${BASE_URL}/api/products`);
    url.searchParams.set("limit", "50");
    if (category && category !== "All") {
      url.searchParams.set("category", category);
    }
    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.products || [];
  } catch (err) {
    console.error("Failed to fetch products:", err);
    return [];
  }
}

export async function sendChatMessage(
  message: string,
  chatHistory: Array<{ role: string; content: string }>
): Promise<{
  reply: string;
  chat_history: Array<{ role: string; content: string }>;
  blocked_by_security: boolean;
}> {
  const res = await fetch(`${BASE_URL}/api/agent/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, chat_history: chatHistory }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error (${res.status})`);
  }

  return await res.json();
}

export async function analyzeReviewSentiment(
  review: string
): Promise<SentimentAnalysisResult> {
  const res = await fetch(`${BASE_URL}/api/agent/feedback/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ review }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to analyze review (${res.status})`
    );
  }

  return await res.json();
}

export async function analyzeBatchFeedback(
  reviews: string[],
  maxWorkers = 5
): Promise<BatchAnalysisResult> {
  const res = await fetch(`${BASE_URL}/api/agent/feedback/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reviews, max_workers: maxWorkers }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Batch analysis error (${res.status})`
    );
  }

  return await res.json();
}

// Named Aliases
export const checkHealth = async (): Promise<boolean> => {
  const res = await checkBackendHealth();
  return res.online;
};

export const getProducts = async (): Promise<{ products: Product[] }> => {
  const products = await fetchProducts();
  return { products };
};

export const analyzeFeedback = analyzeReviewSentiment;
export const analyzeFeedbackBatch = analyzeBatchFeedback;
