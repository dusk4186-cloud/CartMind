"""
Unit and integration tests for LangGraph Feedback Controller (FeedbackWorkflowGraph).
Verifies StateGraph compilation, parallel node execution (Task 1 -> Task 2 & Task 3),
streaming, and resilient execution.
"""

import pytest
from app.models.sentiment import (
    SentimentLabel,
    FeedbackType,
    FeedbackCategory,
    RoutingTarget,
    FeedbackPipelineResult,
)
from app.graphs.feedback_graph import FeedbackWorkflowGraph, build_feedback_graph


def test_feedback_graph_compilation():
    """Verify LangGraph StateGraph compiles successfully."""
    graph = build_feedback_graph()
    assert graph is not None


def test_feedback_workflow_graph_invoke_damaged_complaint():
    """Verify LangGraph orchestrates damaged item review to ServiceNow."""
    wf = FeedbackWorkflowGraph()
    res = wf.invoke("The jacket arrived damaged, please replace it.")
    assert isinstance(res, FeedbackPipelineResult)
    assert res.task1.sentiment == SentimentLabel.NEGATIVE
    assert res.task1.categorization == FeedbackType.COMPLAINT
    assert res.task1.feedback_area == FeedbackCategory.QUALITY
    assert len(res.task2.auto_reply_message) > 5
    assert res.task3.routing_target == RoutingTarget.SERVICENOW


def test_feedback_workflow_graph_invoke_delivery_delay():
    """Verify LangGraph orchestrates delivery delay review to Customer Service Email."""
    wf = FeedbackWorkflowGraph()
    res = wf.invoke("My order was delayed by two weeks, what happened?")
    assert isinstance(res, FeedbackPipelineResult)
    assert res.task1.sentiment == SentimentLabel.NEGATIVE
    assert res.task1.categorization == FeedbackType.QUESTION
    assert res.task1.feedback_area == FeedbackCategory.DELIVERY
    assert len(res.task2.auto_reply_message) > 5
    assert res.task3.routing_target == RoutingTarget.CUSTOMER_SERVICE_EMAIL


def test_feedback_workflow_graph_invoke_jira_bug():
    """Verify LangGraph orchestrates app/checkout crash review to Jira."""
    wf = FeedbackWorkflowGraph()
    res = wf.invoke("The checkout bug error 500 crashes whenever I submit payment.")
    assert isinstance(res, FeedbackPipelineResult)
    assert res.task3.routing_target == RoutingTarget.JIRA
    assert "Jira" in res.task3.routing_action


def test_feedback_workflow_graph_invoke_positive_statement():
    """Verify LangGraph handles positive praise with N/A routing."""
    wf = FeedbackWorkflowGraph()
    res = wf.invoke("The leather jacket fits perfectly and feels premium.")
    assert isinstance(res, FeedbackPipelineResult)
    assert res.task1.sentiment == SentimentLabel.POSITIVE
    assert res.task3.routing_target == RoutingTarget.NOT_APPLICABLE


def test_feedback_workflow_graph_stream_steps():
    """Verify LangGraph step streaming yields intermediate node state updates."""
    wf = FeedbackWorkflowGraph()
    steps = list(wf.stream_steps("The jacket arrived damaged, please replace it."))
    assert len(steps) >= 2
    # Ensure at least one step contains task1 and later steps contain task2 or task3
    step_keys = set()
    for s in steps:
        step_keys.update(s.keys())
    assert "classify" in step_keys


def test_feedback_workflow_mermaid_diagram():
    """Verify Mermaid diagram generation for architectural inspection."""
    diagram = FeedbackWorkflowGraph.get_mermaid_diagram()
    assert "classify" in diagram
    assert "auto_reply" in diagram
    assert "routing" in diagram
    assert "START" in diagram
    assert "END" in diagram


def test_feedback_workflow_graph_batch_execution():
    """Verify concurrent batch execution across multiple reviews with aggregated metrics."""
    from app.models.sentiment import BatchFeedbackResult
    wf = FeedbackWorkflowGraph()
    sample_reviews = [
        "Great shoes, if you love trekking",
        "The shoes are great, if you enjoy blisters",
        "The jacket arrived damaged, please replace it.",
    ]
    batch_res = wf.batch(sample_reviews, max_workers=3)
    assert isinstance(batch_res, BatchFeedbackResult)
    assert batch_res.total_processed == 3
    assert len(batch_res.results) == 3
    assert "positive" in batch_res.sentiment_distribution
    assert "sarcastic" in batch_res.sentiment_distribution
    assert batch_res.escalations_count >= 1
    assert batch_res.processing_time_ms > 0


def test_lazy_graph_compilation_and_singleton():
    """Verify StateGraph compilation is deferred until accessed and singleton is cached."""
    from app.graphs.feedback_graph import FeedbackWorkflowGraph, get_feedback_workflow

    wf = FeedbackWorkflowGraph()
    # Before accessing compiled_graph or invoking, _compiled_graph is None
    assert wf._compiled_graph is None

    # Accessing .compiled_graph triggers lazy compilation
    compiled = wf.compiled_graph
    assert compiled is not None
    assert wf._compiled_graph is compiled

    # Singleton function returns a valid cached workflow
    s1 = get_feedback_workflow()
    s2 = get_feedback_workflow()
    assert s1 is s2
    assert isinstance(s1, FeedbackWorkflowGraph)


def test_lazy_agent_llm_initialization():
    """Verify LLM initialization in agents is deferred until .llm property access."""
    from app.chains.feedback_tasks import (
        Task1ClassificationAgent,
        Task2AutoReplyAgent,
        Task3RoutingAgent,
    )

    t1 = Task1ClassificationAgent()
    assert t1._llm is None
    # Accessing .llm property triggers lazy instantiation
    llm1 = t1.llm
    assert t1._llm is llm1

    t2 = Task2AutoReplyAgent()
    assert t2._llm is None
    llm2 = t2.llm
    assert t2._llm is llm2

    t3 = Task3RoutingAgent()
    assert t3._llm is None
    llm3 = t3.llm
    assert t3._llm is llm3


def test_langsmith_configuration():
    """Verify LangSmith configuration properties and environment resolution."""
    from app.config import AgentConfig

    assert AgentConfig.is_langsmith_enabled() is True
    assert AgentConfig.get_langsmith_project() == "ecommerce-cx-intelligence"
    key = AgentConfig.get_langsmith_api_key()
    assert key is not None
    assert key.startswith("lsv2_")

    summary = AgentConfig.get_safe_summary()
    assert summary["langsmith_enabled"] is True
    assert summary["langsmith_project"] == "ecommerce-cx-intelligence"

