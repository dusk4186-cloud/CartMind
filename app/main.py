"""
Main FastAPI application entry point for the Mock E-Commerce API.
Provides mock e-commerce backend capabilities optimized as agentic tools.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.data.mock_data import PRODUCTS, REVIEWS
from app.routers import (
    products_router,
    pricing_router,
    reviews_router,
    availability_router,
    search_router,
    sentiment_router,
    support_router,
    feedback_router,
    agent_router,
)


def validate_catalog_integrity() -> None:
    """
    Validates mock data consistency on application startup:
    - Product ID uniqueness
    - Consistent pricing and discount calculation
    - Correct stock quantity to availability status mapping
    - Valid review associations and rating ranges
    """
    seen_ids = set()
    for product in PRODUCTS:
        pid = product["product_id"]
        if pid in seen_ids:
            raise ValueError(f"Duplicate product_id detected: {pid}")
        seen_ids.add(pid)

        # Validate price integrity
        orig = product["original_price"]
        curr = product["price"]
        if curr > orig:
            raise ValueError(f"Selling price ({curr}) exceeds original price ({orig}) for {pid}")

        expected_discount = round(((orig - curr) / orig) * 100, 2)
        if abs(product["discount_percentage"] - expected_discount) > 0.05:
            raise ValueError(f"Discount percentage mismatch for {pid}: {product['discount_percentage']} vs {expected_discount}")

        # Validate stock quantity vs status
        qty = product["stock_quantity"]
        status = product["availability_status"]
        if qty > 5 and status != "in_stock":
            raise ValueError(f"Stock {qty} for {pid} should be 'in_stock', found '{status}'")
        elif 1 <= qty <= 5 and status != "low_stock":
            raise ValueError(f"Stock {qty} for {pid} should be 'low_stock', found '{status}'")
        elif qty == 0 and status != "out_of_stock":
            raise ValueError(f"Stock {qty} for {pid} should be 'out_of_stock', found '{status}'")

    # Validate reviews
    for rev in REVIEWS:
        if rev["product_id"] not in seen_ids:
            raise ValueError(f"Review {rev['review_id']} points to nonexistent product {rev['product_id']}")
        if not (1.0 <= rev["rating"] <= 5.0):
            raise ValueError(f"Review {rev['review_id']} has out-of-range rating {rev['rating']}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup validation."""
    validate_catalog_integrity()
    yield


app = FastAPI(
    title="Mock E-Commerce API for Agentic AI Smart Search",
    description=(
        "Simulated e-commerce backend providing hardcoded realistic catalogue, "
        "pricing breakdown, customer reviews, stock inventory availability, "
        "and smart multi-attribute product search. Designed specifically for tool "
        "exposure to Agentic AI shopping assistants."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS for local testing and AI web interfaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def clean_empty_query_params(request, call_next):
    """
    Middleware that intercepts query strings and removes empty/blank parameters.
    In Swagger UI, when optional input fields are left empty or cleared, the browser sends
    empty strings (e.g. `?sort_by=&min_price=`), which cause 422 parsing errors.
    This strips empty parameters so they are treated as omitted (None).
    """
    from urllib.parse import parse_qsl, urlencode

    query_string = request.scope.get("query_string", b"").decode("utf-8")
    if query_string:
        pairs = parse_qsl(query_string, keep_blank_values=True)
        cleaned = [(k, v) for k, v in pairs if v.strip() != ""]
        request.scope["query_string"] = urlencode(cleaned).encode("utf-8")
    return await call_next(request)

# Register route modules
app.include_router(products_router)
app.include_router(pricing_router)
app.include_router(reviews_router)
app.include_router(availability_router)
app.include_router(search_router)
app.include_router(sentiment_router)
app.include_router(support_router)
app.include_router(feedback_router)
app.include_router(agent_router)


@app.get(
    "/",
    tags=["Root"],
    summary="API Root and Tool Index",
    description="Returns service metadata and links to available tool endpoints for AI agents.",
)
def root() -> Dict[str, Any]:
    """Root endpoint welcoming clients and listing core tools."""
    return {
        "name": "Mock E-Commerce API for Agentic AI",
        "version": "1.0.0",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "endpoints": {
            "catalogue": "GET /api/products",
            "product_details": "GET /api/products/{product_id}",
            "pricing": "GET /api/products/{product_id}/price",
            "reviews": "GET /api/products/{product_id}/reviews",
            "availability": "GET /api/products/{product_id}/availability",
            "smart_search": "GET /api/search",
            "sentiment": "GET /api/products/{product_id}/sentiment",
            "escalate_support": "POST /api/support/escalate",
            "classify_feedback": "POST /api/feedback/classify",
            "feedback_samples": "GET /api/feedback/samples",
        },
        "total_catalog_items": len(PRODUCTS),
        "total_customer_reviews": len(REVIEWS),
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Reports API health status and loaded dataset statistics.",
)
def health_check() -> Dict[str, Any]:
    """Provides operational health confirmation and mock database size."""
    return {
        "status": "healthy",
        "catalog_size": len(PRODUCTS),
        "reviews_count": len(REVIEWS),
    }
