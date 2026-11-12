"""
LangChain tools for the E-Commerce Agentic Smart Search application.
Wraps the existing FastAPI backend endpoints with parameter validation and structured outputs.
"""

from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.api_client import EcommerceAPIClient
from app.output_sanitizer import sanitize_system_metadata

# Shared default client instance
_client = EcommerceAPIClient()


def get_api_client() -> EcommerceAPIClient:
    """Returns the active API client instance."""
    return _client


def set_api_client(client: EcommerceAPIClient) -> None:
    """Sets custom API client (useful for mock testing)."""
    global _client
    _client = client


class SearchProductsInput(BaseModel):
    """Input parameters for smart product search."""
    query: Optional[str] = Field(
        None,
        description="Search text or keywords (e.g. 'comfortable running shoes', 'leather wallet')",
    )
    category: Optional[str] = Field(
        None,
        description="Product category filter: 'Belts', 'Shoes', 'Wallets', or 'Jackets'",
    )
    brand: Optional[str] = Field(
        None,
        description="Brand filter (e.g. 'Puma', 'Woodland', 'Wildhorn', 'Bata', 'Levi\\'s', 'Tommy Hilfiger')",
    )
    min_price: Optional[float] = Field(
        None,
        ge=0,
        description="Minimum product price in INR",
    )
    max_price: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum product price in INR (e.g. 3000.0 for 'under 3000')",
    )
    min_rating: Optional[float] = Field(
        None,
        ge=1.0,
        le=5.0,
        description="Minimum average customer rating (1.0 to 5.0, e.g. 4.0 for 'at least 4 stars')",
    )
    available_only: bool = Field(
        False,
        description="Set to True to exclude out-of-stock items (quantity > 0)",
    )
    sort_by: Optional[str] = Field(
        None,
        description="Sort criteria: 'price_asc' (lowest price), 'price_desc' (highest price), or 'rating_desc'",
    )
    preferred_color: Optional[str] = Field(
        None,
        description="Specific color required by user (e.g. 'Black', 'Brown', 'Navy')",
    )
    preferred_size: Optional[str] = Field(
        None,
        description="Specific size required by user (e.g. '8', '9', 'M', 'L', '34')",
    )
    limit: int = Field(
        10,
        ge=1,
        le=50,
        description="Maximum number of candidate products to return",
    )


class CatalogueInput(BaseModel):
    """Input parameters for browsing product catalogue."""
    category: Optional[str] = Field(
        None,
        description="Filter by category ('Belts', 'Shoes', 'Wallets', 'Jackets')",
    )
    brand: Optional[str] = Field(
        None,
        description="Filter by brand name",
    )
    min_price: Optional[float] = Field(None, description="Minimum price boundary")
    max_price: Optional[float] = Field(None, description="Maximum price boundary")
    min_rating: Optional[float] = Field(None, description="Minimum average rating")
    keyword: Optional[str] = Field(None, description="Keyword substring match")
    skip: int = Field(0, description="Pagination offset")
    limit: int = Field(10, description="Maximum items per page")


class ProductIDInput(BaseModel):
    """Input parameter for product-specific lookups."""
    product_id: str = Field(
        ...,
        description="Exact product ID (e.g. 'PROD001', 'PROD007')",
    )


class ReviewsInput(BaseModel):
    """Input parameters for customer reviews retrieval."""
    product_id: str = Field(
        ...,
        description="Target product ID (e.g. 'PROD001')",
    )
    min_rating: Optional[float] = Field(
        None,
        ge=1.0,
        le=5.0,
        description="Only return reviews with this minimum rating (1.0 to 5.0)",
    )
    limit: int = Field(10, description="Maximum reviews to fetch")


class EscalateToHumanInput(BaseModel):
    """Input parameters for escalating a shopper issue to human support agents."""
    issue_summary: str = Field(
        ...,
        description="Clear, concise summary of the customer's issue or dispute requiring human intervention",
    )
    category: Optional[str] = Field(
        "other",
        description=(
            "Reason category: 'explicit_human_request', 'billing_or_payment_dispute', "
            "'order_damage_or_missing', 'high_frustration', 'policy_exception', or 'other'"
        ),
    )
    urgency: Optional[str] = Field(
        "medium",
        description="Urgency priority level: 'low', 'medium', 'high', or 'critical'",
    )
    customer_query: Optional[str] = Field(
        None,
        description="The shopper's verbatim query or complaint statement",
    )
    product_id: Optional[str] = Field(
        None,
        description="Related product ID if the issue pertains to a specific catalogue item",
    )


# ============================================================================
# Tool 1: Product Search

# ============================================================================
@tool(args_schema=SearchProductsInput)
def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    available_only: bool = False,
    sort_by: Optional[str] = None,
    preferred_color: Optional[str] = None,
    preferred_size: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Search the e-commerce product catalogue for products matching keywords and filters.
    Use this tool whenever the user is looking for products, shopping options, or wants to explore items.
    Supports filtering by category, brand, budget/price range, rating, availability, color, and size.
    """
    res = _client.search_products(
        query=query,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        available_only=available_only,
        sort_by=sort_by,
        limit=limit,
    )

    if not res.get("success"):
        return {"error": res.get("message", "Search failed"), "products": []}

    data = res["data"]
    products: List[Dict[str, Any]] = data.get("products", [])

    # Client-side filtering for color preference when specified
    if preferred_color:
        color_norm = preferred_color.strip().lower()
        products = [
            p for p in products
            if any(color_norm in c.lower() for c in p.get("available_colors", []))
        ]

    # Client-side filtering for size preference when specified
    if preferred_size:
        size_norm = preferred_size.strip().lower()
        products = [
            p for p in products
            if any(size_norm == s.lower() or size_norm in s.lower() for s in p.get("available_sizes", []))
        ]

    return {
        "total_matches": len(products),
        "products": products[:limit],
        "applied_filters": data.get("applied_filters", {}),
    }


# ============================================================================
# Tool 2: Product Catalogue
# ============================================================================
@tool(args_schema=CatalogueInput)
def get_product_catalogue(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    keyword: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Retrieve and paginate the complete product catalogue.
    Use this when browsing general store inventory or inspecting all items in a category without a search query.
    """
    res = _client.get_product_catalogue(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )

    if not res.get("success"):
        return {"error": res.get("message", "Catalogue retrieval failed"), "products": []}

    return res["data"]


# ============================================================================
# Tool 3: Product Details
# ============================================================================
@tool(args_schema=ProductIDInput)
def get_product_details(product_id: str) -> Dict[str, Any]:
    """
    Retrieve complete specification, description, category, and attributes for a single product ID.
    Use this when you know the product_id (e.g. 'PROD001') and need deep specifications.
    """
    res = _client.get_product_details(product_id)
    if not res.get("success"):
        return {"error": res.get("message", f"Product '{product_id}' not found")}
    return res["data"]


# ============================================================================
# Tool 4: Product Pricing
# ============================================================================
@tool(args_schema=ProductIDInput)
def get_product_pricing(product_id: str) -> Dict[str, Any]:
    """
    Retrieve verified pricing breakdown for a product, including current selling price, original price,
    discount percentage, and currency.
    Use this tool when answering price questions or evaluating discounts.
    """
    res = _client.get_product_pricing(product_id)
    if not res.get("success"):
        return {"error": res.get("message", f"Pricing for '{product_id}' not found")}
    return res["data"]


# ============================================================================
# Tool 5: Customer Reviews
# ============================================================================
@tool(args_schema=ReviewsInput)
def get_customer_reviews(
    product_id: str,
    min_rating: Optional[float] = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """
    Retrieve authentic customer reviews, ratings, and feedback comments for a specific product ID.
    Use this tool to analyze customer sentiment, extract genuine pros and cons, and verify user experience.
    """
    res = _client.get_product_reviews(product_id, min_rating=min_rating, limit=limit)
    if not res.get("success"):
        return {"error": res.get("message", f"Reviews for '{product_id}' not found"), "reviews": []}
    return res["data"]


# ============================================================================
# Tool 6: Product Availability
# ============================================================================
@tool(args_schema=ProductIDInput)
def get_product_availability(product_id: str) -> Dict[str, Any]:
    """
    Check real-time stock inventory, stock status ('in_stock', 'low_stock', 'out_of_stock'),
    units remaining, and currently available sizes and colors for a product ID.
    Always use this before confirming a product is available for purchase.
    """
    res = _client.get_product_availability(product_id)
    if not res.get("success"):
        return {"error": res.get("message", f"Availability for '{product_id}' not found")}
    return res["data"]


# ============================================================================
# Tool 7: Product Sentiment & Sarcasm Breakdown
# ============================================================================
@tool(args_schema=ProductIDInput)
def analyze_product_sentiment(product_id: str) -> Dict[str, Any]:
    """
    Perform deep sentiment analysis, sarcasm detection, and review aspect breakdown for a specific product ID.
    Returns overall sentiment category (positive, negative, neutral, sarcastic, mixed),
    distribution percentages, key customer praises, genuine complaints, and flagged sarcastic comments.
    Use this tool when users ask:
    - 'What are customers really saying about this product?'
    - 'Are there any complaints or sarcastic reviews?'
    - 'What is the sentiment or satisfaction breakdown?'
    """
    res = _client.get_product_sentiment(product_id)
    if not res.get("success"):
        return {"error": res.get("message", f"Sentiment analysis for '{product_id}' not found")}
    return res["data"]


# ============================================================================
# Tool 8: Escalate to Human Support
# ============================================================================
@tool(args_schema=EscalateToHumanInput)
def escalate_to_human_support(
    issue_summary: str,
    category: Optional[str] = "other",
    urgency: Optional[str] = "medium",
    customer_query: Optional[str] = None,
    product_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Escalate a customer issue or request to human support agents and generate an authoritative support ticket.
    Use this tool when:
    - The shopper explicitly requests a human representative, live agent, manager, or supervisor.
    - The shopper reports a billing dispute, double charge, payment failure with money debited, or refund issue.
    - The shopper reports a damaged package, broken item upon delivery, missing package, or empty box.
    - The shopper expresses severe frustration, legal threats, or calls the service a scam/fraud.
    - The shopper has a B2B, bulk order, or policy exception beyond automated shopping assistance.
    Returns generated support ticket details including ticket ID, assigned department, estimated wait time,
    and priority helpline contact information.
    """
    res = _client.escalate_to_human_support(
        issue_summary=issue_summary,
        category=category,
        urgency=urgency,
        customer_query=customer_query,
        product_id=product_id,
    )
    if not res.get("success"):
        return {"error": res.get("message", "Human escalation request failed")}
    return res["data"]


class ClassifyFeedbackInput(BaseModel):
    """Input parameters for classifying customer feedback or review statements."""
    feedback_text: str = Field(
        ...,
        description="The customer's feedback, review comment, or message text to classify",
    )
    review_id: Optional[str] = Field(
        None,
        description="Optional review identifier (e.g. 'REVIEW 03')",
    )


# ============================================================================
# Tool 9: Classify Customer Feedback
# ============================================================================
@tool(args_schema=ClassifyFeedbackInput)
def classify_customer_feedback(
    feedback_text: str,
    review_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Classify customer feedback or review comment across multi-dimensional criteria (Sentiment, Intent, Aspect, Routing).
    Use this tool ONLY when explicitly asked to analyze customer reviews, evaluate feedback, or diagnose a customer support ticket.
    Do NOT use this tool for normal shopping questions, product searches, price inquiries, or stock availability checks.
    """
    res = _client.classify_feedback(text=feedback_text, review_id=review_id)
    if not res.get("success"):
        return {"error": res.get("message", "Feedback classification failed")}
    return res["data"]


# ============================================================================
# Tool 10: Smart Shopping Lookup (Output-Sanitized Query Tool)
# ============================================================================
@tool
def smart_shopping_lookup(user_query: str) -> str:
    """Query the e-commerce backend for product availability and metrics with sanitized output."""
    # 1. Fetch raw data from backend
    raw_res = _client.search_products(query=user_query, limit=5)
    raw_backend_response = str(raw_res)

    # 2. CLEARLY SEPARATE user-facing data from system metadata
    # Do NOT pass function schemas or system metadata array strings back to the LLM
    sanitized_response = sanitize_system_metadata(raw_backend_response)

    return sanitized_response


ALL_TOOLS = [
    search_products,
    get_product_catalogue,
    get_product_details,
    get_product_pricing,
    get_customer_reviews,
    get_product_availability,
    analyze_product_sentiment,
    escalate_to_human_support,
    classify_customer_feedback,
    smart_shopping_lookup,
]



