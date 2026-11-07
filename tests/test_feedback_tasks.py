"""
Comprehensive test suite for the 3 LangChain Customer Feedback agents:
  • Task 1: Task1ClassificationAgent (Review -> Sentiment, Categorization, Feedback Area)
  • Task 2: Task2AutoReplyAgent (Review + Op/Task 1 -> Auto reply message)
  • Task 3: Task3RoutingAgent (Review + Op/Task 1 -> Routing action: Jira, ServiceNow, Customer service email, N/A)
  • End-to-end: run_feedback_pipeline
"""

import pytest
from app.models.sentiment import (
    SentimentLabel,
    FeedbackType,
    FeedbackCategory,
    RoutingTarget,
    Task1ClassificationOutput,
    Task2AutoReplyOutput,
    Task3RoutingOutput,
    FeedbackPipelineResult,
)
from app.chains.feedback_tasks import (
    Task1ClassificationAgent,
    Task2AutoReplyAgent,
    Task3RoutingAgent,
    run_feedback_pipeline,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. TASK 1 AGENT TESTS: CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def test_task1_agent_positive_statement():
    """Verify Task 1 classifies wallet review into positive statement."""
    agent = Task1ClassificationAgent()
    out = agent.invoke({"review": "Absolutely love this brand! The wallet I bought is stylish and durable."})
    assert isinstance(out, Task1ClassificationOutput)
    assert out.sentiment == SentimentLabel.POSITIVE
    assert out.categorization in (FeedbackType.STATEMENT, FeedbackType.PRAISE)


def test_task1_agent_damaged_complaint():
    """Verify Task 1 classifies damaged jacket as a Quality Complaint."""
    agent = Task1ClassificationAgent()
    out = agent.invoke({"review": "The jacket arrived damaged, please replace it."})
    assert isinstance(out, Task1ClassificationOutput)
    assert out.sentiment == SentimentLabel.NEGATIVE
    assert out.categorization == FeedbackType.COMPLAINT
    assert out.feedback_area == FeedbackCategory.QUALITY
    assert out.commentary is not None


def test_task1_agent_delayed_delivery_question():
    """Verify Task 1 classifies delayed order as a Delivery Question."""
    agent = Task1ClassificationAgent()
    out = agent.invoke({"review": "My order was delayed by two weeks, what happened?"})
    assert isinstance(out, Task1ClassificationOutput)
    assert out.sentiment == SentimentLabel.NEGATIVE
    assert out.categorization == FeedbackType.QUESTION
    assert out.feedback_area == FeedbackCategory.DELIVERY


# ─────────────────────────────────────────────────────────────────────────────
# 2. TASK 2 AGENT TESTS: AUTO REPLY GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def test_task2_agent_complaint_auto_reply():
    """Verify Task 2 generates an empathetic apology and resolution commitment."""
    agent = Task2AutoReplyAgent()
    inputs = {
        "review": "The jacket arrived damaged, please replace it.",
        "sentiment": "negative",
        "categorization": "Complaint",
        "feedback_area": "Quality",
    }
    out = agent.invoke(inputs)
    assert isinstance(out, Task2AutoReplyOutput)
    assert len(out.auto_reply_message) > 10
    assert any(w in out.auto_reply_message.lower() for w in ["sorry", "apologize", "resolve", "replacement"])


def test_task2_agent_positive_auto_reply():
    """Verify Task 2 generates a warm appreciation message for praise/statement."""
    agent = Task2AutoReplyAgent()
    inputs = {
        "review": "The leather jacket fits perfectly and feels premium.",
        "sentiment": "positive",
        "categorization": "Statement",
        "feedback_area": "N/A",
    }
    out = agent.invoke(inputs)
    assert isinstance(out, Task2AutoReplyOutput)
    assert len(out.auto_reply_message) > 10
    assert any(w in out.auto_reply_message.lower() for w in ["thank", "appreciate", "glad", "happy"])


# ─────────────────────────────────────────────────────────────────────────────
# 3. TASK 3 AGENT TESTS: WORKFLOW ROUTING (Jira, ServiceNow, Customer service email)
# ─────────────────────────────────────────────────────────────────────────────

def test_task3_agent_servicenow_escalation():
    """Verify Task 3 routes physical damage and replacement requests to ServiceNow."""
    agent = Task3RoutingAgent()
    inputs = {
        "review": "The jacket arrived damaged, please replace it.",
        "sentiment": "negative",
        "categorization": "Complaint",
        "feedback_area": "Quality",
    }
    out = agent.invoke(inputs)
    assert isinstance(out, Task3RoutingOutput)
    assert out.routing_target == RoutingTarget.SERVICENOW
    assert "ServiceNow" in out.routing_action
    assert out.priority in ("high", "critical")


def test_task3_agent_customer_service_email():
    """Verify Task 3 routes logistics / shipping delay questions to Customer Service Email."""
    agent = Task3RoutingAgent()
    inputs = {
        "review": "My order was delayed by two weeks, what happened?",
        "sentiment": "negative",
        "categorization": "Question",
        "feedback_area": "Delivery",
    }
    out = agent.invoke(inputs)
    assert isinstance(out, Task3RoutingOutput)
    assert out.routing_target == RoutingTarget.CUSTOMER_SERVICE_EMAIL
    assert any(w in out.routing_action.lower() for w in ["support", "forward", "customer service"])


def test_task3_agent_jira_bug_ticket():
    """Verify Task 3 routes technical platform / checkout bugs to Jira."""
    agent = Task3RoutingAgent()
    inputs = {
        "review": "The checkout bug error 500 crashes whenever I submit payment.",
        "sentiment": "negative",
        "categorization": "Complaint",
        "feedback_area": "Quality",
    }
    out = agent.invoke(inputs)
    assert isinstance(out, Task3RoutingOutput)
    assert out.routing_target == RoutingTarget.JIRA
    assert "Jira" in out.routing_action


def test_task3_agent_no_routing_needed_for_praise():
    """Verify Task 3 does not escalate positive praise statements."""
    agent = Task3RoutingAgent()
    inputs = {
        "review": "Absolutely love this brand! The wallet I bought is stylish and durable.",
        "sentiment": "positive",
        "categorization": "Statement",
        "feedback_area": "N/A",
    }
    out = agent.invoke(inputs)
    assert isinstance(out, Task3RoutingOutput)
    assert out.routing_target == RoutingTarget.NOT_APPLICABLE
    assert out.routing_action == "N/A"


# ─────────────────────────────────────────────────────────────────────────────
# 4. END-TO-END FEEDBACK PIPELINE EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

def test_run_feedback_pipeline_canonical_reviews():
    """Verify end-to-end pipeline execution chaining Task 1 -> Task 2 & Task 3."""
    res = run_feedback_pipeline("The jacket arrived damaged, please replace it.")
    assert isinstance(res, FeedbackPipelineResult)
    assert res.review == "The jacket arrived damaged, please replace it."
    # Task 1 checks
    assert res.task1.sentiment == SentimentLabel.NEGATIVE
    assert res.task1.categorization == FeedbackType.COMPLAINT
    assert res.task1.feedback_area == FeedbackCategory.QUALITY
    # Task 2 checks
    assert len(res.task2.auto_reply_message) > 5
    # Task 3 checks
    assert res.task3.routing_target == RoutingTarget.SERVICENOW
    assert "ServiceNow" in res.task3.routing_action


def test_sarcastic_blisters_feedback_pipeline():
    """Verify end-to-end pipeline correctly recognizes sarcastic review with blisters as a complaint."""
    res = run_feedback_pipeline("The shoes are great, if you enjoy blisters")
    assert isinstance(res, FeedbackPipelineResult)
    # Task 1: Must be sarcastic, complaint, sizing
    assert res.task1.sentiment in (SentimentLabel.SARCASTIC, SentimentLabel.NEGATIVE)
    assert res.task1.categorization == FeedbackType.COMPLAINT
    assert res.task1.feedback_area == FeedbackCategory.SIZING
    # Task 2: Empathy & apology, never cheerful praise
    assert "glad you enjoyed" not in res.task2.auto_reply_message.lower()
    assert any(w in res.task2.auto_reply_message.lower() for w in ["apologize", "sorry", "discomfort", "return", "exchange"])
    # Task 3: Escalated to customer support email or ServiceNow, never N/A
    assert res.task3.routing_target in (RoutingTarget.CUSTOMER_SERVICE_EMAIL, RoutingTarget.SERVICENOW)
    assert res.task3.routing_action != "N/A"
