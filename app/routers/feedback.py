"""
API router for customer feedback classification, intent diagnosis, and routing action assignment.
Matches the Customer Experience (CX) Intelligence dashboard specifications.
"""

from typing import List, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.models.sentiment import (
    FeedbackClassification,
    FeedbackPipelineResult,
    BatchFeedbackRequest,
    BatchFeedbackResult,
)
from app.services.sentiment_service import SentimentService

router = APIRouter(prefix="/api/feedback", tags=["Customer Feedback Classification"])


class ClassifyFeedbackRequest(BaseModel):
    """Payload for classifying customer feedback or review comment."""
    text: str = Field(..., description="Customer feedback or review comment text")
    review_id: Optional[str] = Field(default=None, description="Optional review/feedback ID (e.g. 'REVIEW 03')")
    feedback_id: Optional[str] = Field(default=None, description="Alternative alias for review_id")


@router.post(
    "/classify",
    response_model=FeedbackClassification,
    status_code=status.HTTP_200_OK,
    summary="Classify Customer Feedback Intent & Aspect",
    description=(
        "Analyzes feedback text and extracts Sentiment (positive, negative, neutral, sarcastic), "
        "Feedback Type (Statement, Complaint, Question, Praise, Suggestion), Aspect Category "
        "(Quality, Delivery, Pricing, Sizing, Customer Service, N/A), diagnostic commentary, "
        "a tailored suggested response, and an operational routing decision."
    ),
)
def classify_feedback_endpoint(request: ClassifyFeedbackRequest) -> FeedbackClassification:
    """Classify arbitrary customer feedback statement into structured CX intelligence."""
    target_id = request.review_id or request.feedback_id
    return SentimentService.classify_feedback(request.text, review_id=target_id)


@router.get(
    "/samples",
    response_model=List[FeedbackClassification],
    summary="Get Canonical Feedback Sample Cards",
    description="Returns pre-classified customer feedback cards matching the CX intelligence dashboard view.",
)
def get_feedback_samples() -> List[FeedbackClassification]:
    """Retrieve canonical sample cards for UI dashboard rendering."""
    return SentimentService.get_sample_feedback_cards()


@router.post(
    "/workflow",
    response_model=FeedbackPipelineResult,
    status_code=status.HTTP_200_OK,
    summary="Execute LangGraph 3-Agent Feedback Workflow",
    description=(
        "Executes the full LangGraph controller pipeline across 3 decoupled LangChain agents: "
        "Task 1 (Classification), Task 2 (Auto-Reply), and Task 3 (Workflow Routing: Jira/ServiceNow/Customer service email)."
    ),
)
def execute_feedback_workflow_endpoint(request: ClassifyFeedbackRequest) -> FeedbackPipelineResult:
    """Run full LangGraph feedback orchestrator on customer comment."""
    from app.graphs.feedback_graph import get_feedback_workflow
    workflow = get_feedback_workflow()
    return workflow.invoke(request.text)


@router.post(
    "/batch",
    response_model=BatchFeedbackResult,
    status_code=status.HTTP_200_OK,
    summary="Execute Batch Customer Reviews Sentiment Analysis",
    description="Processes a collection of customer reviews concurrently via LangGraph, returning individual results and aggregated analytics.",
)
async def execute_batch_feedback_endpoint(request: BatchFeedbackRequest) -> BatchFeedbackResult:
    """Run concurrent LangGraph batch analysis across customer reviews asynchronously."""
    from app.graphs.feedback_graph import get_feedback_workflow
    workflow = get_feedback_workflow()
    max_workers = request.max_concurrency or 5
    return await workflow.abatch(request.reviews, max_concurrency=max_workers)


@router.get(
    "/workflow/graph",
    summary="Get LangGraph Workflow Topology",
    description="Returns Mermaid diagram string visualizing the 3-agent LangGraph topology.",
)
def get_workflow_topology():
    """Retrieve Mermaid diagram for LangGraph controller architecture."""
    from app.graphs import FeedbackWorkflowGraph
    return {"mermaid": FeedbackWorkflowGraph.get_mermaid_diagram()}
