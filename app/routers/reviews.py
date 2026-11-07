"""
API router for customer reviews and sentiment/rating exploration.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.product import ReviewListResponse, ErrorResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/api/products", tags=["Reviews"])


@router.get(
    "/{product_id}/reviews",
    response_model=ReviewListResponse,
    summary="Get Product Reviews",
    description=(
        "Retrieve customer reviews for a given product. Supports filtering by minimum rating "
        "and pagination. Returns HTTP 404 if the product does not exist, or an empty list if no reviews match."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Customer reviews retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Product not found"},
        422: {"model": ErrorResponse, "description": "Invalid query parameters"},
    },
)
def get_product_reviews(
    product_id: str,
    min_rating: Optional[float] = Query(
        None,
        ge=1.0,
        le=5.0,
        description="Filter reviews having at least this rating (1.0 to 5.0)",
        examples=[4.0],
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of reviews to skip for pagination",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of reviews to return (1-100)",
    ),
) -> ReviewListResponse:
    """Retrieve customer feedback and ratings for a product."""
    review_data = ReviewService.get_product_reviews(
        product_id=product_id,
        min_rating=min_rating,
        skip=skip,
        limit=limit,
    )

    if review_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    reviews, total = review_data

    return ReviewListResponse(
        product_id=product_id,
        total_reviews=total,
        skip=skip,
        limit=limit,
        reviews=reviews,
    )
