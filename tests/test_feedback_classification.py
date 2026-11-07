"""
Unit and integration tests for customer feedback classification and diagnostic commentary.
Verifies intent classification (Complaint, Question, Statement, Praise, Suggestion),
aspect categorization, suggested response generation, and workflow routing actions.
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.sentiment import (
    SentimentLabel,
    FeedbackType,
    FeedbackCategory,
    FeedbackRoutingAction,
    FeedbackClassification,
)
from app.services.sentiment_service import SentimentService
from app.api_client import EcommerceAPIClient
from app.tools import classify_customer_feedback, set_api_client, get_api_client

client = TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
# 1. CANONICAL FEEDBACK CLASSIFICATION TESTS (MATCHING SPEC SPECIFICATION)
# ─────────────────────────────────────────────────────────────────────────────

def test_classify_positive_wallet_statement():
    """Verify REVIEW 01: Positive Statement regarding style/durability with N/A routing."""
    text = "Absolutely love this brand! The wallet I bought is stylish and durable."
    card = SentimentService.classify_feedback(text, review_id="REVIEW 01")
    assert card.feedback_id == "REVIEW 01"
    assert card.sentiment == SentimentLabel.POSITIVE
    assert card.feedback_type == FeedbackType.STATEMENT
    assert card.category == FeedbackCategory.NOT_APPLICABLE
    assert "Thank you for your feedback!" in card.suggested_response
    assert card.routing_action == FeedbackRoutingAction.NOT_APPLICABLE
    assert card.needs_escalation is False
    assert "Statement" in card.commentary


def test_classify_positive_jacket_statement():
    """Verify REVIEW 02: Positive Statement regarding fit/premium feel with N/A routing."""
    text = "The leather jacket fits perfectly and feels premium."
    card = SentimentService.classify_feedback(text, review_id="REVIEW 02")
    assert card.feedback_id == "REVIEW 02"
    assert card.sentiment == SentimentLabel.POSITIVE
    assert card.feedback_type == FeedbackType.STATEMENT
    assert card.category == FeedbackCategory.NOT_APPLICABLE
    assert "We appreciate your kind words! Happy you loved it." in card.suggested_response
    assert card.routing_action == FeedbackRoutingAction.NOT_APPLICABLE
    assert card.needs_escalation is False


def test_classify_damaged_jacket_complaint():
    """Verify REVIEW 03: Negative Quality Complaint with ServiceNow escalation routing."""
    text = "The jacket arrived damaged, please replace it."
    card = SentimentService.classify_feedback(text, review_id="REVIEW 03")
    assert card.feedback_id == "REVIEW 03"
    assert card.sentiment == SentimentLabel.NEGATIVE
    assert card.feedback_type == FeedbackType.COMPLAINT
    assert card.category == FeedbackCategory.QUALITY
    assert "We're sorry for the issue. We'll resolve this promptly." in card.suggested_response
    assert card.routing_action == FeedbackRoutingAction.SERVICENOW_ESCALATION
    assert card.needs_escalation is True
    assert "Quality" in card.commentary


def test_classify_delayed_order_question():
    """Verify REVIEW 04: Delivery Question with Forward to support engineer routing."""
    text = "My order was delayed by two weeks, what happened?"
    card = SentimentService.classify_feedback(text, review_id="REVIEW 04")
    assert card.feedback_id == "REVIEW 04"
    assert card.sentiment == SentimentLabel.NEGATIVE
    assert card.feedback_type == FeedbackType.QUESTION
    assert card.category == FeedbackCategory.DELIVERY
    assert "We apologize for the delay. We're investigating this matter." in card.suggested_response
    assert card.routing_action == FeedbackRoutingAction.FORWARD_TO_SUPPORT_ENGINEER
    assert card.needs_escalation is True
    assert "Delivery" in card.commentary


def test_classify_sarcastic_shoes_blisters():
    """Verify sarcastic review 'The shoes are great, if you enjoy blisters' is identified as Sarcastic Sizing Complaint."""
    text = "The shoes are great, if you enjoy blisters"
    card = SentimentService.classify_feedback(text)
    assert card.sentiment == SentimentLabel.SARCASTIC
    assert card.feedback_type == FeedbackType.COMPLAINT
    assert card.category == FeedbackCategory.SIZING
    assert "blisters" in card.suggested_response.lower() or "discomfort" in card.suggested_response.lower() or "apologize" in card.suggested_response.lower()
    assert "glad you enjoyed" not in card.suggested_response.lower()
    assert card.routing_action == FeedbackRoutingAction.FORWARD_TO_SUPPORT_ENGINEER
    assert card.needs_escalation is True
    assert "sarcastic" in card.commentary.lower() or "blister" in card.commentary.lower()


def test_classify_trekking_shoes_genuine_positive():
    """Verify 'Great shoes, if you love trekking' is recognized as genuine positive praise, not sarcasm."""
    text = "Great shoes, if you love trekking"
    card = SentimentService.classify_feedback(text)
    assert card.sentiment == SentimentLabel.POSITIVE
    assert card.feedback_type == FeedbackType.STATEMENT
    assert card.category == FeedbackCategory.NOT_APPLICABLE
    assert card.routing_action == FeedbackRoutingAction.NOT_APPLICABLE
    assert card.needs_escalation is False
    assert "glad you enjoyed" in card.suggested_response.lower() or "thank you" in card.suggested_response.lower()


def test_classify_ants_biting_waist_belt_sarcastic_complaint():
    """Verify 'This belt is so good, feeling like ants biting my waist' is recognized as Sarcastic Sizing Complaint."""
    text = "This belt is so good, feeling like ants biting my waist"
    card = SentimentService.classify_feedback(text)
    assert card.sentiment == SentimentLabel.SARCASTIC
    assert card.feedback_type == FeedbackType.COMPLAINT
    assert card.category == FeedbackCategory.SIZING
    assert card.routing_action == FeedbackRoutingAction.FORWARD_TO_SUPPORT_ENGINEER
    assert card.needs_escalation is True
    assert "discomfort" in card.suggested_response.lower() or "apologize" in card.suggested_response.lower()


def test_get_sample_feedback_cards_length():
    """Verify sample feedback cards generator returns all 4 canonical cards."""
    samples = SentimentService.get_sample_feedback_cards()
    assert len(samples) == 4
    assert samples[0].feedback_id == "REVIEW 01"
    assert samples[1].feedback_id == "REVIEW 02"
    assert samples[2].feedback_id == "REVIEW 03"
    assert samples[3].feedback_id == "REVIEW 04"


# ─────────────────────────────────────────────────────────────────────────────
# 2. FASTAPI FEEDBACK ROUTER TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_api_classify_feedback_endpoint_success():
    """Verify POST /api/feedback/classify returns 200 with structured classification."""
    payload = {
        "text": "The jacket arrived damaged, please replace it.",
        "review_id": "REVIEW 03",
    }
    response = client.post("/api/feedback/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["feedback_id"] == "REVIEW 03"
    assert data["feedback_type"] == "Complaint"
    assert data["category"] == "Quality"
    assert data["routing_action"] == "ServiceNow escalation"
    assert data["needs_escalation"] is True


def test_api_get_feedback_samples_success():
    """Verify GET /api/feedback/samples returns 200 and list of 4 cards."""
    response = client.get("/api/feedback/samples")
    assert response.status_code == 200
    cards = response.json()
    assert len(cards) == 4
    assert cards[2]["feedback_type"] == "Complaint"
    assert cards[3]["feedback_type"] == "Question"


def test_api_workflow_endpoint_success():
    """Verify POST /api/feedback/workflow executes LangGraph workflow controller."""
    payload = {"text": "The jacket arrived damaged, please replace it."}
    response = client.post("/api/feedback/workflow", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["task1"]["sentiment"] == "negative"
    assert data["task1"]["categorization"] == "Complaint"
    assert data["task3"]["routing_target"] == "ServiceNow"


def test_api_batch_feedback_endpoint_success():
    """Verify POST /api/feedback/batch processes multiple reviews concurrently."""
    payload = {
        "reviews": [
            "Great shoes, if you love trekking",
            "The shoes are great, if you enjoy blisters",
        ],
        "max_concurrency": 2,
    }
    response = client.post("/api/feedback/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_processed"] == 2
    assert len(data["results"]) == 2
    assert "positive" in data["sentiment_distribution"]
    assert "sarcastic" in data["sentiment_distribution"]
    assert data["processing_time_ms"] > 0



def test_api_workflow_graph_success():
    """Verify GET /api/feedback/workflow/graph returns Mermaid topology."""
    response = client.get("/api/feedback/workflow/graph")
    assert response.status_code == 200
    assert "mermaid" in response.json()
    assert "classify" in response.json()["mermaid"]


# ─────────────────────────────────────────────────────────────────────────────
# 3. LANGCHAIN TOOL TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_langchain_classify_customer_feedback_mock():
    """Verify classify_customer_feedback tool invokes client and returns diagnosis."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.classify_feedback.return_value = {
        "success": True,
        "data": {
            "feedback_id": "TEST_01",
            "text": "The jacket arrived damaged, please replace it.",
            "sentiment": "negative",
            "feedback_type": "Complaint",
            "category": "Quality",
            "commentary": "Customer reported damaged shipment requiring replacement.",
            "suggested_response": "We’re sorry for the issue. We’ll resolve this promptly.",
            "routing_action": "ServiceNow escalation",
            "needs_escalation": True,
        },
    }

    orig_client = get_api_client()
    try:
        set_api_client(mock_client)
        result = classify_customer_feedback.invoke({
            "feedback_text": "The jacket arrived damaged, please replace it.",
            "review_id": "TEST_01",
        })
        assert result["feedback_type"] == "Complaint"
        assert result["category"] == "Quality"
        assert result["routing_action"] == "ServiceNow escalation"
        mock_client.classify_feedback.assert_called_once()
    finally:
        set_api_client(orig_client)
