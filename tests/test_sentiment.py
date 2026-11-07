"""
Automated unit and integration test suite for Sentiment Analysis, Sarcasm Detection,
FastAPI sentiment endpoint, and LangChain sentiment tool.
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api_client import EcommerceAPIClient
from app.models.sentiment import SentimentLabel, ReviewSentiment, ProductSentimentSummary
from app.services.sentiment_service import SentimentService
from app.tools import analyze_product_sentiment, set_api_client, get_api_client

client = TestClient(app)



# ─────────────────────────────────────────────────────────────────────────────
# 1. INDIVIDUAL REVIEW SENTIMENT & SARCASM CLASSIFICATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_classify_positive_review():
    """Verify classification of enthusiastic positive customer feedback."""
    review = {
        "review_id": "TEST_POS_1",
        "reviewer_name": "Happy Customer",
        "rating": 5.0,
        "comment": "Exceptional genuine leather quality. Love the reversible swivel buckle mechanism, perfect finish!",
    }
    result = SentimentService.classify_review(review)
    assert result.sentiment == SentimentLabel.POSITIVE
    assert result.sentiment_score > 0
    assert result.confidence >= 0.8
    assert result.is_sarcastic is False
    assert "quality" in result.key_aspects or "buckle" in result.key_aspects


def test_classify_negative_review():
    """Verify classification of critical negative customer complaint."""
    review = {
        "review_id": "TEST_NEG_1",
        "reviewer_name": "Unhappy Buyer",
        "rating": 1.5,
        "comment": "Material feels like cheap cardboard and tore after two days. Horrible quality, complete waste.",
    }
    result = SentimentService.classify_review(review)
    assert result.sentiment == SentimentLabel.NEGATIVE
    assert result.sentiment_score < 0
    assert result.confidence >= 0.8
    assert result.is_sarcastic is False


def test_classify_neutral_review():
    """Verify classification of matter-of-fact neutral customer feedback."""
    review = {
        "review_id": "TEST_NEU_1",
        "reviewer_name": "Neutral Shopper",
        "rating": 3.0,
        "comment": "Decent everyday belt. Standard canvas strap, neither too heavy nor too light.",
    }
    result = SentimentService.classify_review(review)
    assert result.sentiment == SentimentLabel.NEUTRAL
    assert -0.5 <= result.sentiment_score <= 0.5


def test_classify_sarcastic_review_rating_mismatch():
    """Verify sarcasm detection when low star rating is paired with hyperbolic praise words."""
    review = {
        "review_id": "TEST_SARC_1",
        "reviewer_name": "Ironic Reviewer",
        "rating": 1.5,
        "comment": "Lightning fast delivery, took only 3 weeks to arrive! Truly amazing quality.",
    }
    result = SentimentService.classify_review(review)
    assert result.is_sarcastic is True
    assert result.sentiment == SentimentLabel.SARCASTIC
    assert result.sentiment_score < 0
    assert result.confidence >= 0.85


def test_classify_sarcastic_review_phrasing():
    """Verify sarcasm detection via idiomatic sarcastic phrases ('what a brilliant design', 'great if you enjoy')."""
    review = {
        "review_id": "TEST_SARC_2",
        "reviewer_name": "Frustrated Sarcastic",
        "rating": 2.0,
        "comment": "What a brilliant design! Elastic stretched out permanently. Great if you enjoy pulling up your pants every five minutes.",
    }
    result = SentimentService.classify_review(review)
    assert result.is_sarcastic is True
    assert result.sentiment == SentimentLabel.SARCASTIC


def test_classify_mixed_review():
    """Verify mixed review detection containing both positive praise and contrastive complaints."""
    review = {
        "review_id": "TEST_MIX_1",
        "reviewer_name": "Balanced Buyer",
        "rating": 3.5,
        "comment": "Great durable leather at this discount price, but the buckle is a bit stiff and heavy.",
    }
    result = SentimentService.classify_review(review)
    assert result.sentiment == SentimentLabel.MIXED
    assert result.confidence >= 0.8


# ─────────────────────────────────────────────────────────────────────────────
# 2. PRODUCT AGGREGATION & SUMMARY TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_product_sentiment_summary_aggregation():
    """Verify product-level sentiment calculation, percentages, and tone guidance."""
    summary = SentimentService.analyze_product_reviews("PROD001")
    assert summary is not None
    assert summary.product_id == "PROD001"
    assert summary.total_reviews_analyzed >= 4
    assert summary.positive_percentage > 50.0
    assert "positive" in summary.sentiment_distribution
    assert len(summary.key_praises) > 0
    assert len(summary.recommended_agent_tone) > 0


def test_product_sentiment_summary_with_sarcasm_flagging():
    """Verify product summary correctly isolates and flags sarcastic reviews (e.g. PROD019)."""
    summary = SentimentService.analyze_product_reviews("PROD019")
    assert summary is not None
    assert summary.sentiment_distribution["sarcastic"] >= 1
    assert summary.sarcastic_percentage > 0
    assert len(summary.sarcastic_warnings) >= 1
    assert any("Sarcasm" in w for w in summary.sarcastic_warnings)


def test_product_sentiment_nonexistent_product_returns_none():
    """Verify non-existent product returns None for 404 handling."""
    summary = SentimentService.analyze_product_reviews("NONEXISTENT_999")
    assert summary is None


# ─────────────────────────────────────────────────────────────────────────────
# 3. LIVE USER CHAT SENTIMENT & TONE ADAPTATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_user_query_sarcasm_detection():
    """Verify detection of shopper sarcasm in chat and empathetic tone guidance generation."""
    query = "Great job on having zero size 9 shoes in stock, truly amazing service!"
    result = SentimentService.analyze_user_query(query)
    assert result.is_sarcastic is True
    assert result.sentiment == SentimentLabel.SARCASTIC
    assert "DO NOT take sarcastic praise literally" in result.tone_advice


def test_user_query_high_frustration():
    """Verify detection of high customer frustration and calm de-escalation tone guidance."""
    query = "This is ridiculous and terrible, why is everything I want out of stock?!"
    result = SentimentService.analyze_user_query(query)
    assert result.frustration_level == "high"
    assert result.sentiment == SentimentLabel.NEGATIVE
    assert "empathetic" in result.tone_advice.lower()


def test_user_query_positive_intent():
    """Verify detection of positive shopper enthusiasm and engaging tone guidance."""
    query = "Awesome, I love these running shoes! Can you check if size 10 is available?"
    result = SentimentService.analyze_user_query(query)
    assert result.sentiment == SentimentLabel.POSITIVE
    assert result.frustration_level == "none"
    assert result.is_sarcastic is False


def test_user_query_neutral_discovery():
    """Verify neutral user query maintains direct, objective tone advice."""
    query = "Show me all black leather belts under 1500 rupees."
    result = SentimentService.analyze_user_query(query)
    assert result.sentiment == SentimentLabel.NEUTRAL
    assert result.frustration_level == "none"


# ─────────────────────────────────────────────────────────────────────────────
# 4. FASTAPI SENTIMENT ROUTER TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_api_get_product_sentiment_success():
    """Verify GET /api/products/{id}/sentiment returns 200 with structured summary."""
    response = client.get("/api/products/PROD001/sentiment")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "PROD001"
    assert "overall_sentiment" in data
    assert "sentiment_distribution" in data
    assert "positive_percentage" in data
    assert "key_praises" in data
    assert "recommended_agent_tone" in data


def test_api_get_product_sentiment_not_found():
    """Verify GET /api/products/{id}/sentiment returns 404 for invalid product ID."""
    response = client.get("/api/products/PROD999_INVALID/sentiment")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# 5. LANGCHAIN TOOL INTEGRATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_langchain_analyze_product_sentiment_tool_success():
    """Verify analyze_product_sentiment LangChain tool invocation and mapping."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.get_product_sentiment.return_value = {
        "success": True,
        "data": {
            "product_id": "PROD001",
            "overall_sentiment": "positive",
            "sentiment_distribution": {"positive": 3, "negative": 0},
            "positive_percentage": 100.0,
            "recommended_agent_tone": "Upbeat and confident",
        },
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        result = analyze_product_sentiment.invoke({"product_id": "PROD001"})
        mock_client.get_product_sentiment.assert_called_once_with("PROD001")
        assert isinstance(result, dict)
        assert result.get("product_id") == "PROD001"
        assert result.get("overall_sentiment") == "positive"
    finally:
        set_api_client(original_client)


def test_langchain_analyze_product_sentiment_tool_handles_error():
    """Verify analyze_product_sentiment LangChain tool handles missing product safely."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.get_product_sentiment.return_value = {
        "success": False,
        "message": "Product with ID 'INVALID_PROD_ID' not found.",
        "status_code": 404,
    }

    original_client = get_api_client()
    try:
        set_api_client(mock_client)
        result = analyze_product_sentiment.invoke({"product_id": "INVALID_PROD_ID"})
        assert isinstance(result, dict)
        assert "error" in result
    finally:
        set_api_client(original_client)

