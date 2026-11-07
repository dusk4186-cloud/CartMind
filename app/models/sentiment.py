"""
Pydantic data models for sentiment and sarcasm analysis.
Covers product review sentiment breakdowns and live conversational user feedback classification.
"""

from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class SentimentLabel(str, Enum):
    """Classification categories for sentiment analysis."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    SARCASTIC = "sarcastic"
    MIXED = "mixed"


class EscalationReason(str, Enum):
    """Categories requiring human support handover."""
    EXPLICIT_HUMAN_REQUEST = "explicit_human_request"
    BILLING_OR_PAYMENT_DISPUTE = "billing_or_payment_dispute"
    ORDER_DAMAGE_OR_MISSING = "order_damage_or_missing"
    HIGH_FRUSTRATION = "high_frustration"
    POLICY_EXCEPTION = "policy_exception"
    OTHER = "other"


class EscalationUrgency(str, Enum):
    """Priority urgency level for human support routing."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackType(str, Enum):
    """Classified communicative intent of customer feedback."""
    STATEMENT = "Statement"
    COMPLAINT = "Complaint"
    QUESTION = "Question"
    PRAISE = "Praise"
    SUGGESTION = "Suggestion"


class FeedbackCategory(str, Enum):
    """Domain category or product aspect addressed by feedback."""
    QUALITY = "Quality"
    DELIVERY = "Delivery"
    PRICING = "Pricing"
    SIZING = "Sizing"
    CUSTOMER_SERVICE = "Customer Service"
    NOT_APPLICABLE = "N/A"


class RoutingTarget(str, Enum):
    """External platform destination for actionable customer feedback routing."""
    SERVICENOW = "ServiceNow"
    CUSTOMER_SERVICE_EMAIL = "Customer service email"
    JIRA = "Jira"
    NOT_APPLICABLE = "N/A"


class FeedbackRoutingAction(str, Enum):
    """Operational workflow routing recommendation for customer feedback."""
    NOT_APPLICABLE = "N/A"
    SERVICENOW_ESCALATION = "ServiceNow escalation"
    FORWARD_TO_SUPPORT_ENGINEER = "Forward to customer support engineer"
    JIRA_BUG_TICKET = "Jira bug ticket"
    BILLING_SPECIALIST_HANDOVER = "Billing specialist handover"
    STORE_OPERATIONS_REVIEW = "Store operations review"



class ReviewSentiment(BaseModel):
    """Sentiment classification result for an individual customer review."""
    review_id: str = Field(..., description="Unique review identifier")
    reviewer_name: str = Field(..., description="Reviewer name")
    rating: float = Field(..., description="Original customer star rating")
    comment: str = Field(..., description="Customer feedback comment text")
    sentiment: SentimentLabel = Field(..., description="Categorized sentiment label")
    sentiment_score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Continuous valence score from -1.0 (very negative) to +1.0 (very positive)",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of classification from 0.0 to 1.0",
    )
    is_sarcastic: bool = Field(
        default=False,
        description="True if sarcasm or ironic hyperbole is detected in the comment",
    )
    key_aspects: List[str] = Field(
        default_factory=list,
        description="Key product aspects mentioned (e.g. 'quality', 'durability', 'sizing', 'price')",
    )


class ProductSentimentSummary(BaseModel):
    """Aggregated sentiment breakdown across all customer reviews for a product."""
    product_id: str = Field(..., description="Product identifier (e.g. PROD001)")
    product_name: str = Field(default="", description="Name of the product")
    total_reviews_analyzed: int = Field(..., description="Number of reviews evaluated")
    overall_sentiment: SentimentLabel = Field(..., description="Dominant sentiment label")
    average_sentiment_score: float = Field(..., description="Mean sentiment score (-1.0 to 1.0)")
    sentiment_distribution: Dict[str, int] = Field(
        ...,
        description="Count of reviews per sentiment category",
    )
    positive_percentage: float = Field(..., description="Percentage of positive reviews")
    negative_percentage: float = Field(..., description="Percentage of negative reviews")
    neutral_percentage: float = Field(..., description="Percentage of neutral reviews")
    sarcastic_percentage: float = Field(..., description="Percentage of sarcastic reviews")
    mixed_percentage: float = Field(..., description="Percentage of mixed reviews")
    key_praises: List[str] = Field(
        default_factory=list,
        description="Verified customer praise points extracted from positive feedback",
    )
    key_complaints: List[str] = Field(
        default_factory=list,
        description="Verified customer complaints extracted from negative feedback",
    )
    sarcastic_warnings: List[str] = Field(
        default_factory=list,
        description="Flagged sarcastic comments translated into honest customer complaints",
    )
    recommended_agent_tone: str = Field(
        ...,
        description="Guidance for agent tone when discussing this product (e.g. 'Highlight quality, caution about sizing')",
    )


class UserFeedbackSentiment(BaseModel):
    """Sentiment, frustration, and human-in-the-loop escalation assessment of shopper input."""
    query: str = Field(..., description="The user's query or feedback message")
    sentiment: SentimentLabel = Field(..., description="Detected sentiment of user")
    is_sarcastic: bool = Field(default=False, description="Whether the user is being sarcastic/ironic")
    frustration_level: str = Field(
        default="none",
        description="Frustration level: 'none', 'mild', or 'high'",
    )
    needs_human_escalation: bool = Field(
        default=False,
        description="True if the user's issue exceeds automated scope or requires human support intervention",
    )
    escalation_reason: Optional[EscalationReason] = Field(
        default=None,
        description="Primary reason for escalating to a human support agent",
    )
    escalation_urgency: Optional[EscalationUrgency] = Field(
        default=None,
        description="Priority urgency level for support queue routing",
    )
    tone_advice: str = Field(
        ...,
        description="Actionable instruction for the agent's conversational tone to address user state",
    )
    feedback_type: Optional[FeedbackType] = Field(
        default=None,
        description="Classified communicative intent of the feedback (Statement, Complaint, Question, Praise, Suggestion)",
    )
    category: Optional[FeedbackCategory] = Field(
        default=None,
        description="Domain category or product aspect addressed (Quality, Delivery, Pricing, Sizing, Customer Service, N/A)",
    )
    feedback_commentary: Optional[str] = Field(
        default=None,
        description="Agent analysis and commentary explaining the nature and context of the feedback",
    )
    suggested_response: Optional[str] = Field(
        default=None,
        description="Empathetic, actionable suggested response tailored to the feedback type",
    )
    routing_action: Optional[FeedbackRoutingAction] = Field(
        default=None,
        description="Recommended operational routing action (e.g. 'ServiceNow escalation', 'N/A')",
    )


class FeedbackClassification(BaseModel):
    """Authoritative feedback classification card schema matching the CX intelligence dashboard."""
    feedback_id: Optional[str] = Field(default=None, description="Review/Feedback identifier (e.g. 'REVIEW 03')")
    text: str = Field(..., description="The verbatim customer feedback or review comment")
    sentiment: SentimentLabel = Field(..., description="Detected sentiment: positive, negative, neutral, sarcastic")
    feedback_type: FeedbackType = Field(..., description="Classified intent: Statement, Complaint, Question, Praise, Suggestion")
    category: FeedbackCategory = Field(..., description="Aspect / department: Quality, Delivery, Pricing, Sizing, Customer Service, N/A")
    commentary: str = Field(..., description="Diagnostic commentary explaining the nature of the feedback")
    suggested_response: str = Field(..., description="Recommended empathetic canned or generative response")
    routing_action: FeedbackRoutingAction = Field(..., description="Actionable routing decision (e.g. 'ServiceNow escalation', 'N/A')")
    needs_escalation: bool = Field(default=False, description="True if feedback triggers an automated support ticket or human escalation")



class SupportTicketRequest(BaseModel):
    """Customer support escalation handover request payload."""
    issue_summary: str = Field(..., description="Concise summary of the customer's problem or request")
    category: EscalationReason = Field(
        default=EscalationReason.OTHER,
        description="Category / reason for support escalation",
    )
    urgency: EscalationUrgency = Field(
        default=EscalationUrgency.MEDIUM,
        description="Urgency priority of the escalation",
    )
    customer_query: Optional[str] = Field(
        default=None,
        description="Original user message or verbatim feedback",
    )
    product_id: Optional[str] = Field(
        default=None,
        description="Associated product ID (e.g. 'PROD001') if issue relates to a specific item",
    )


class SupportTicket(BaseModel):
    """Simulated authoritative support ticket generated upon human escalation handover."""
    ticket_id: str = Field(..., description="Unique generated ticket identifier (e.g. TKT-9821)")
    category: EscalationReason = Field(..., description="Escalation category")
    urgency: EscalationUrgency = Field(..., description="Assigned urgency level")
    issue_summary: str = Field(..., description="Summary of customer issue")
    status: str = Field(default="OPEN", description="Ticket workflow status (OPEN, ASSIGNED, ESCALATED)")
    estimated_wait_minutes: int = Field(
        ...,
        description="Estimated response wait time in minutes for human representative connection",
    )
    assigned_team: str = Field(
        ...,
        description="Specialized support department assigned to resolve the ticket",
    )
    support_phone: str = Field(
        default="+1 (800) 555-0199",
        description="Toll-free customer support helpline phone number",
    )
    support_email: str = Field(
        default="support@smartstore.example.com",
        description="Dedicated customer support email address",
    )
    created_at: str = Field(..., description="ISO 8601 timestamp of ticket creation")


# ─────────────────────────────────────────────────────────────────────────────
# 3-TASK LANGCHAIN & LANGGRAPH PIPELINE SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class Task1ClassificationOutput(BaseModel):
    """
    Task 1 Output: Structured classification of customer review into Sentiment,
    Categorization (Intent), and Feedback Area.
    """
    sentiment: SentimentLabel = Field(
        ...,
        description="Customer sentiment polarity (positive, negative, neutral, sarcastic, mixed)",
    )
    categorization: FeedbackType = Field(
        ...,
        description="Categorization of review intent (Statement, Complaint, Question, Praise, Suggestion)",
    )
    feedback_area: FeedbackCategory = Field(
        ...,
        description="Specific domain feedback area (Quality, Delivery, Pricing, Sizing, Customer Service, N/A)",
    )
    commentary: Optional[str] = Field(
        default=None,
        description="Diagnostic analysis commenting on the type of feedback and implications",
    )


class Task2AutoReplyOutput(BaseModel):
    """
    Task 2 Output: Generated auto-reply message formulated from the review
    and the output of Task 1.
    """
    auto_reply_message: str = Field(
        ...,
        description="Empathetic, context-tailored suggested response message to the reviewer",
    )


class Task3RoutingOutput(BaseModel):
    """
    Task 3 Output: Actionable workflow routing decision determining target platform
    (Jira, ServiceNow, Customer service email, or N/A).
    """
    routing_action: str = Field(
        ...,
        description="Workflow action label (e.g. 'ServiceNow escalation', 'Forward to customer support engineer', 'Jira bug ticket')",
    )
    routing_target: RoutingTarget = Field(
        ...,
        description="Designated destination platform (ServiceNow, Jira, Customer service email, N/A)",
    )
    priority: str = Field(
        default="medium",
        description="Urgency priority (critical, high, medium, low, none)",
    )
    reason: str = Field(
        ...,
        description="Diagnostic reasoning explaining the routing decision based on Review + Task 1 output",
    )


class FeedbackPipelineResult(BaseModel):
    """Combined result from all 3 LangChain tasks under LangGraph orchestration."""
    review: str = Field(..., description="Original raw review/feedback text")
    task1: Task1ClassificationOutput = Field(..., description="Classification output from Task 1")
    task2: Task2AutoReplyOutput = Field(..., description="Auto reply message from Task 2")
    task3: Task3RoutingOutput = Field(..., description="Workflow routing action from Task 3")


class BatchFeedbackRequest(BaseModel):
    """Payload for submitting multiple customer reviews for concurrent batch sentiment analysis."""
    reviews: List[str] = Field(..., description="List of review text comments to process in batch")
    max_concurrency: Optional[int] = Field(default=5, description="Maximum concurrent worker threads for processing")


class BatchFeedbackResult(BaseModel):
    """Aggregated analytical summary and per-item outputs for a batch of reviews."""
    total_processed: int = Field(..., description="Total number of reviews analyzed")
    results: List[FeedbackPipelineResult] = Field(..., description="Individual pipeline results for each review")
    sentiment_distribution: Dict[str, int] = Field(..., description="Counts grouped by sentiment (positive, negative, sarcastic, etc.)")
    category_distribution: Dict[str, int] = Field(..., description="Counts grouped by aspect area (Quality, Delivery, Sizing, etc.)")
    routing_distribution: Dict[str, int] = Field(..., description="Counts grouped by destination (ServiceNow, Jira, Email, N/A)")
    escalations_count: int = Field(..., description="Count of reviews requiring operational escalation")
    processing_time_ms: float = Field(..., description="Total batch processing latency in milliseconds")

