"""
Comprehensive unit and integration tests for Human-in-the-Loop (HITL) support escalation.
Tests trigger conditions, ticket generation, FastAPI /api/support/escalate endpoint,
and the LangChain escalate_to_human_support tool.
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.sentiment import (
    EscalationReason,
    EscalationUrgency,
    SupportTicketRequest,
    SupportTicket,
)
from app.services.sentiment_service import SentimentService
from app.api_client import EcommerceAPIClient
from app.tools import escalate_to_human_support, set_api_client, get_api_client

client = TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
# 1. ESCALATION TRIGGER & DETECTION TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_escalation_explicit_human_request():
    """Verify user asking for human agent triggers EXPLICIT_HUMAN_REQUEST escalation."""
    query = "Can I please speak to a human representative? The bot isn't understanding me."
    sentiment = SentimentService.analyze_user_query(query)
    assert sentiment.needs_human_escalation is True
    assert sentiment.escalation_reason == EscalationReason.EXPLICIT_HUMAN_REQUEST
    assert sentiment.escalation_urgency == EscalationUrgency.MEDIUM
    assert "escalate_to_human_support" in sentiment.tone_advice


def test_escalation_frustrated_human_request():
    """Verify frustrated user demanding a manager/supervisor escalates with HIGH urgency."""
    query = "I'm fed up with this useless bot, transfer me to a supervisor right now!!"
    sentiment = SentimentService.analyze_user_query(query)
    assert sentiment.needs_human_escalation is True
    assert sentiment.escalation_reason == EscalationReason.EXPLICIT_HUMAN_REQUEST
    assert sentiment.escalation_urgency == EscalationUrgency.HIGH


def test_escalation_billing_dispute():
    """Verify payment failure / double charge / refund issues trigger BILLING_OR_PAYMENT_DISPUTE."""
    query = "I was charged twice on my credit card for my purchase! Where is my refund?"
    sentiment = SentimentService.analyze_user_query(query)
    assert sentiment.needs_human_escalation is True
    assert sentiment.escalation_reason == EscalationReason.BILLING_OR_PAYMENT_DISPUTE
    assert sentiment.escalation_urgency == EscalationUrgency.HIGH


def test_escalation_damaged_or_missing_goods():
    """Verify damaged box or missing parcel reports trigger ORDER_DAMAGE_OR_MISSING."""
    query = "My shoes arrived broken and the parcel was completely damaged."
    sentiment = SentimentService.analyze_user_query(query)
    assert sentiment.needs_human_escalation is True
    assert sentiment.escalation_reason == EscalationReason.ORDER_DAMAGE_OR_MISSING
    assert sentiment.escalation_urgency == EscalationUrgency.HIGH


def test_escalation_legal_threat_or_scam_allegation():
    """Verify legal threats trigger HIGH_FRUSTRATION with CRITICAL urgency."""
    query = "You guys are scammers, I am going to report this to consumer court and sue you!"
    sentiment = SentimentService.analyze_user_query(query)
    assert sentiment.needs_human_escalation is True
    assert sentiment.escalation_reason == EscalationReason.HIGH_FRUSTRATION
    assert sentiment.escalation_urgency == EscalationUrgency.CRITICAL


def test_escalation_policy_exception_bulk_order():
    """Verify B2B / bulk purchase inquiries trigger POLICY_EXCEPTION."""
    query = "We want to place a bulk order of 250 leather jackets for our company employees."
    sentiment = SentimentService.analyze_user_query(query)
    assert sentiment.needs_human_escalation is True
    assert sentiment.escalation_reason == EscalationReason.POLICY_EXCEPTION
    assert sentiment.escalation_urgency == EscalationUrgency.MEDIUM


def test_no_escalation_for_normal_shopping():
    """Verify routine shopping query does NOT trigger human escalation."""
    query = "What is the price of the Wildhorn RFID leather wallet?"
    sentiment = SentimentService.analyze_user_query(query)
    assert sentiment.needs_human_escalation is False
    assert sentiment.escalation_reason is None


# ─────────────────────────────────────────────────────────────────────────────
# 2. SUPPORT TICKET CREATION LOGIC TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_create_support_ticket_billing():
    """Verify creation of billing support ticket with appropriate team routing and wait time."""
    req = SupportTicketRequest(
        issue_summary="Customer charged twice on Visa card ending in 4021",
        category=EscalationReason.BILLING_OR_PAYMENT_DISPUTE,
        urgency=EscalationUrgency.HIGH,
        customer_query="Double deduction on credit card",
        product_id="PROD005",
    )
    ticket = SentimentService.create_support_ticket(req)
    assert ticket.ticket_id.startswith("TKT-")
    assert ticket.category == EscalationReason.BILLING_OR_PAYMENT_DISPUTE
    assert ticket.urgency == EscalationUrgency.HIGH
    assert ticket.assigned_team == "Billing & Financial Reconciliation"
    assert ticket.estimated_wait_minutes == 5
    assert ticket.status == "OPEN"
    assert ticket.support_phone is not None
    assert ticket.support_email is not None


def test_create_support_ticket_critical():
    """Verify critical escalation assigns shortest estimated wait time (3 minutes)."""
    req = SupportTicketRequest(
        issue_summary="Customer threatening legal action over non-delivery",
        category=EscalationReason.HIGH_FRUSTRATION,
        urgency=EscalationUrgency.CRITICAL,
    )
    ticket = SentimentService.create_support_ticket(req)
    assert ticket.assigned_team == "Executive Customer Relations"
    assert ticket.estimated_wait_minutes == 3


# ─────────────────────────────────────────────────────────────────────────────
# 3. FASTAPI SUPPORT ROUTER TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_api_escalate_support_success():
    """Verify POST /api/support/escalate creates a support ticket and returns HTTP 201."""
    payload = {
        "issue_summary": "Item delivered was the wrong color and size",
        "category": "order_damage_or_missing",
        "urgency": "high",
        "customer_query": "I received brown shoes instead of black",
        "product_id": "PROD003",
    }
    response = client.post("/api/support/escalate", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_id"].startswith("TKT-")
    assert data["category"] == "order_damage_or_missing"
    assert data["urgency"] == "high"
    assert data["status"] == "OPEN"
    assert "Logistics" in data["assigned_team"]
    assert data["estimated_wait_minutes"] == 5


def test_api_escalate_support_validation_error():
    """Verify POST /api/support/escalate returns 422 if required issue_summary is missing."""
    response = client.post("/api/support/escalate", json={})
    assert response.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# 4. LANGCHAIN TOOL TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_langchain_escalate_to_human_tool_mock():
    """Verify escalate_to_human_support tool interacts cleanly with API client."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.escalate_to_human_support.return_value = {
        "success": True,
        "data": {
            "ticket_id": "TKT-49102",
            "category": "explicit_human_request",
            "urgency": "medium",
            "issue_summary": "User wants to speak with a human",
            "status": "OPEN",
            "estimated_wait_minutes": 10,
            "assigned_team": "Live Customer Care",
            "support_phone": "+1 (800) 555-0199",
            "support_email": "support@smartstore.example.com",
            "created_at": "2026-10-16T17:00:00Z",
        },
    }

    orig_client = get_api_client()
    try:
        set_api_client(mock_client)
        result = escalate_to_human_support.invoke({
            "issue_summary": "User wants to speak with a human",
            "category": "explicit_human_request",
            "urgency": "medium",
        })
        assert result["ticket_id"] == "TKT-49102"
        assert result["assigned_team"] == "Live Customer Care"
        assert result["estimated_wait_minutes"] == 10
        mock_client.escalate_to_human_support.assert_called_once()
    finally:
        set_api_client(orig_client)


def test_langchain_escalate_to_human_tool_handles_error():
    """Verify tool handles client failures gracefully."""
    mock_client = MagicMock(spec=EcommerceAPIClient)
    mock_client.escalate_to_human_support.return_value = {
        "success": False,
        "message": "Connection refused by support service",
    }

    orig_client = get_api_client()
    try:
        set_api_client(mock_client)
        result = escalate_to_human_support.invoke({
            "issue_summary": "Disputed transaction",
            "category": "billing_or_payment_dispute",
            "urgency": "high",
        })
        assert "error" in result
        assert "Connection refused" in result["error"]
    finally:
        set_api_client(orig_client)
