"""
Automated unit and integration tests for LangChain tools and HTTP API client.
Covers tool-to-endpoint mapping, filtering, error handling, timeouts, and live execution.
"""

import socket
import pytest
from unittest.mock import MagicMock
from app.api_client import EcommerceAPIClient


def is_backend_running(host="127.0.0.1", port=8000) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False
from app.tools import (
    search_products,
    get_product_catalogue,
    get_product_details,
    get_product_pricing,
    get_customer_reviews,
    get_product_availability,
    analyze_product_sentiment,
    escalate_to_human_support,
    set_api_client,
    get_api_client,
)


# ============================================================================
# 1. Tool-to-Endpoint Mapping and Parameter Forwarding
# ============================================================================
def test_search_products_tool_mapping():
    """Verify search_products tool maps correctly to client and filters results."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.search_products.return_value = {
        "success": True,
        "data": {
            "total": 2,
            "products": [
                {
                    "product_id": "PROD007",
                    "name": "Air Stride Lightweight Running Shoes",
                    "price": 2699.0,
                    "available_colors": ["Jet Black", "Cool Grey"],
                    "available_sizes": ["8", "9", "10"],
                },
                {
                    "product_id": "PROD008",
                    "name": "Oxford Handcrafted Formal Derby Leather Shoes",
                    "price": 2449.0,
                    "available_colors": ["Black", "Brown"],
                    "available_sizes": ["7", "8"],
                },
            ],
            "applied_filters": {"query": "shoes"},
        },
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        result = search_products.invoke({
            "query": "shoes",
            "category": "Shoes",
            "max_price": 3000.0,
            "min_rating": 4.0,
            "available_only": True,
            "preferred_color": "Jet Black",
            "preferred_size": "9",
        })

        # Verify client was called with backend parameters
        mock_client.search_products.assert_called_once_with(
            query="shoes",
            category="Shoes",
            brand=None,
            min_price=None,
            max_price=3000.0,
            min_rating=4.0,
            available_only=True,
            sort_by=None,
            limit=10,
        )

        # Verify client-side color & size filters narrowed it to PROD007
        assert result["total_matches"] == 1
        assert result["products"][0]["product_id"] == "PROD007"
    finally:
        set_api_client(original_client)


def test_get_product_catalogue_tool_mapping():
    """Verify get_product_catalogue calls backend catalogue endpoint."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.get_product_catalogue.return_value = {
        "success": True,
        "data": {"total": 24, "products": [{"product_id": "PROD001"}]},
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        res = get_product_catalogue.invoke({"category": "Belts", "limit": 5})
        mock_client.get_product_catalogue.assert_called_once_with(
            category="Belts",
            brand=None,
            min_price=None,
            max_price=None,
            min_rating=None,
            keyword=None,
            skip=0,
            limit=5,
        )
        assert res["total"] == 24
    finally:
        set_api_client(original_client)


def test_get_product_details_tool_mapping():
    """Verify get_product_details forwards product_id."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.get_product_details.return_value = {
        "success": True,
        "data": {"product_id": "PROD001", "name": "Classic Leather Belt"},
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        res = get_product_details.invoke({"product_id": "PROD001"})
        mock_client.get_product_details.assert_called_once_with("PROD001")
        assert res["product_id"] == "PROD001"
    finally:
        set_api_client(original_client)


def test_get_product_pricing_tool_mapping():
    """Verify get_product_pricing forwards product_id and returns pricing data."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.get_product_pricing.return_value = {
        "success": True,
        "data": {
            "product_id": "PROD001",
            "selling_price": 999.0,
            "original_price": 1999.0,
            "discount_percentage": 50.03,
            "currency": "INR",
        },
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        res = get_product_pricing.invoke({"product_id": "PROD001"})
        mock_client.get_product_pricing.assert_called_once_with("PROD001")
        assert res["selling_price"] == 999.0
        assert res["discount_percentage"] == 50.03
    finally:
        set_api_client(original_client)


def test_get_customer_reviews_tool_mapping():
    """Verify get_customer_reviews forwards product_id and min_rating."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.get_product_reviews.return_value = {
        "success": True,
        "data": {
            "product_id": "PROD001",
            "total_reviews": 3,
            "reviews": [{"reviewer_name": "Aarav", "rating": 5.0}],
        },
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        res = get_customer_reviews.invoke({"product_id": "PROD001", "min_rating": 4.5, "limit": 5})
        mock_client.get_product_reviews.assert_called_once_with("PROD001", min_rating=4.5, limit=5)
        assert res["total_reviews"] == 3
    finally:
        set_api_client(original_client)


def test_get_product_availability_tool_mapping():
    """Verify get_product_availability forwards product_id."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.get_product_availability.return_value = {
        "success": True,
        "data": {
            "product_id": "PROD001",
            "availability_status": "in_stock",
            "stock_quantity": 15,
        },
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        res = get_product_availability.invoke({"product_id": "PROD001"})
        mock_client.get_product_availability.assert_called_once_with("PROD001")
        assert res["availability_status"] == "in_stock"
        assert res["stock_quantity"] == 15
    finally:
        set_api_client(original_client)


# ============================================================================
# 2. Error Handling, Timeouts, and Missing IDs
# ============================================================================
def test_tool_handles_backend_404():
    """Verify tools handle missing products gracefully without crashing."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.get_product_details.return_value = {
        "success": False,
        "error_type": "NOT_FOUND",
        "message": "Product with ID 'PROD999' not found.",
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        res = get_product_details.invoke({"product_id": "PROD999"})
        assert "error" in res
        assert "PROD999" in res["error"]
    finally:
        set_api_client(original_client)


def test_tool_handles_backend_timeout():
    """Verify tools handle backend timeouts gracefully."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.search_products.return_value = {
        "success": False,
        "error_type": "TIMEOUT",
        "message": "Backend request to /api/search timed out after 15.0s.",
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        res = search_products.invoke({"query": "shoes"})
        assert "error" in res
        assert "timed out" in res["error"]
        assert res["products"] == []
    finally:
        set_api_client(original_client)


def test_tool_handles_connection_error():
    """Verify tools handle connection refused gracefully when backend is offline."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.get_product_pricing.return_value = {
        "success": False,
        "error_type": "CONNECTION_ERROR",
        "message": "Could not connect to FastAPI backend at http://127.0.0.1:8000.",
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        res = get_product_pricing.invoke({"product_id": "PROD001"})
        assert "error" in res
        assert "Could not connect" in res["error"]
    finally:
        set_api_client(original_client)


# ============================================================================
# 3. Live Integration Tests against Running FastAPI Backend
# ============================================================================
@pytest.mark.skipif(not is_backend_running(), reason="FastAPI backend not running at http://127.0.0.1:8000")
def test_live_backend_all_tools_integration():
    """Live integration test against running FastAPI backend."""
    live_client = EcommerceAPIClient(base_url="http://127.0.0.1:8000")
    original_client = get_api_client()
    set_api_client(live_client)

    try:
        # Search
        search_res = search_products.invoke({"query": "leather", "max_price": 2000.0})
        assert "products" in search_res
        assert search_res["total_matches"] > 0

        # Details
        details_res = get_product_details.invoke({"product_id": "PROD001"})
        assert details_res.get("product_id") == "PROD001"

        # Pricing
        pricing_res = get_product_pricing.invoke({"product_id": "PROD001"})
        assert pricing_res.get("selling_price") == 999.0

        # Reviews
        reviews_res = get_customer_reviews.invoke({"product_id": "PROD001", "limit": 3})
        assert len(reviews_res.get("reviews", [])) > 0

        # Availability
        avail_res = get_product_availability.invoke({"product_id": "PROD001"})
        assert avail_res.get("availability_status") == "in_stock"

        # Sentiment
        sentiment_res = analyze_product_sentiment.invoke({"product_id": "PROD001"})
        assert sentiment_res.get("product_id") == "PROD001"
        assert "overall_sentiment" in sentiment_res

        # Support Escalation
        escalation_res = escalate_to_human_support.invoke({
            "issue_summary": "Live integration test handover",
            "category": "explicit_human_request",
            "urgency": "medium",
        })
        assert escalation_res.get("ticket_id", "").startswith("TKT-")
        assert escalation_res.get("status") == "OPEN"
    finally:
        set_api_client(original_client)

