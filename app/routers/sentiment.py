"""
API router for customer review sentiment, sarcasm detection, and aspect breakdown.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.sentiment import ProductSentimentSummary
from app.models.product import ErrorResponse
from app.services.sentiment_service import SentimentService

router = APIRouter(prefix="/api/products", tags=["Sentiment Analysis"])


@router.get(
    "/{product_id}/sentiment",
    response_model=ProductSentimentSummary,
    summary="Get Product Review Sentiment & Sarcasm Breakdown",
    description=(
        "Analyzes all customer reviews for a given product ID. Categorizes feedback into positive, "
        "negative, neutral, sarcastic, and mixed sentiments. Surfaces verified praises, common complaints, "
        "and sarcastic remarks translated into authentic feedback."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Sentiment analysis computed successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Product not found"},
    },
)
def get_product_sentiment(product_id: str) -> ProductSentimentSummary:
    """Retrieve deep sentiment analysis and sarcasm detection for a product."""
    summary = SentimentService.analyze_product_reviews(product_id)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )
    return summary
