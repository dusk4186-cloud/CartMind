export interface Product {
  product_id: string;
  name: string;
  category: string;
  brand: string;
  price: number;
  original_price: number;
  discount_percentage: number;
  rating: number;
  review_count: number;
  availability_status: "in_stock" | "low_stock" | "out_of_stock";
  stock_quantity: number;
  sizes?: string[];
  colors?: string[];
  description?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  blockedBySecurity?: boolean;
}

export interface SentimentAnalysisResult {
  review: string;
  sentiment: {
    sentiment: string;
    categorization: string;
    feedback_area: string;
    commentary?: string;
  };
  suggested_response: string;
  routing: {
    routing_target: string;
    routing_action: string;
    priority: string;
    reason?: string;
  };
}

export interface BatchItemResult {
  review: string;
  task1: {
    sentiment: { value: string };
    categorization: { value: string };
    feedback_area: { value: string };
  };
  task2: {
    auto_reply_message: string;
  };
  task3: {
    routing_target: { value: string };
    routing_action: string;
    priority: string;
  };
}

export interface BatchAnalysisResult {
  total_processed: number;
  results: BatchItemResult[];
  sentiment_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  routing_distribution: Record<string, number>;
  escalations_count: number;
  processing_time_ms: number;
}

