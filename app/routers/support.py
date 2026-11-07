"""
API router for Human-in-the-Loop (HITL) support escalation and ticketing handover.
"""

from fastapi import APIRouter, status
from app.models.sentiment import SupportTicketRequest, SupportTicket
from app.services.sentiment_service import SentimentService

router = APIRouter(prefix="/api/support", tags=["Human Support Escalation"])


@router.post(
    "/escalate",
    response_model=SupportTicket,
    status_code=status.HTTP_201_CREATED,
    summary="Escalate Customer Issue to Human Support",
    description=(
        "Generates an authoritative support ticket, routes to the appropriate human support department, "
        "calculates dynamic wait time estimates, and provides direct customer care helpline and email contacts."
    ),
    responses={
        status.HTTP_201_CREATED: {"description": "Support ticket generated and dispatched successfully"},
    },
)
def escalate_issue(request: SupportTicketRequest) -> SupportTicket:
    """Escalate a shopper query or dispute to human support agents."""
    return SentimentService.create_support_ticket(request)
