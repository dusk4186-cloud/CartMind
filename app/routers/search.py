"""
API router for unified smart product search simulating AI assistant retrieval stage.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.product import (
    SearchResponse,
    SortByOption,
    ErrorResponse,
)
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["Search"])

VALID_SORT_OPTIONS = [e.value for e in SortByOption]


@router.get(
    "",
    response_model=SearchResponse,
    summary="Smart Product Search",
    description=(
        "Unified search endpoint designed for AI agent tool integration. "
        "Supports multi-token keyword search, category, brand, price range, "
        "minimum rating, availability filtering, and deterministic sorting."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Matching products and search metadata returned"},
        422: {"model": ErrorResponse, "description": "Invalid parameters or bounds"},
    },
)
def search_products(
    query: Optional[str] = Query(
        None,
        description="Free-text search query (e.g., 'comfortable black shoes')",
    ),
    category: Optional[str] = Query(
        None,
        description="Filter by specific product category (Belts, Shoes, Wallets, Jackets)",
    ),
    brand: Optional[str] = Query(
        None,
        description="Filter by brand name (e.g., Puma, Woodland, Bata)",
    ),
    min_price: Optional[float] = Query(
        None,
        ge=0,
        description="Minimum product price in INR (e.g., 1000.0)",
    ),
    max_price: Optional[float] = Query(
        None,
        ge=0,
        description="Maximum product price in INR (e.g., 3000.0)",
    ),
    min_rating: Optional[float] = Query(
        None,
        ge=1.0,
        le=5.0,
        description="Minimum customer rating 1.0 to 5.0 (e.g., 4.0)",
    ),
    available_only: bool = Query(
        False,
        description="If true, excludes out_of_stock items (quantity > 0)",
    ),
    sort_by: Optional[str] = Query(
        None,
        description="Sort order: 'price_asc', 'price_desc', or 'rating_desc'",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip for pagination",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of records to return (1-100)",
    ),
) -> SearchResponse:
    """Execute multi-attribute product search with relevance scoring and filters."""
    # Validate price bounds
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=422,
            detail="min_price cannot be greater than max_price",
        )

    # Sanitize and validate sort_by
    clean_sort_by = sort_by.strip().lower() if sort_by and sort_by.strip() else None
    if clean_sort_by and clean_sort_by not in VALID_SORT_OPTIONS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid sort_by option '{sort_by}'. "
                f"Allowed values are: {', '.join(VALID_SORT_OPTIONS)}"
            ),
        )

    products, total, applied_filters = SearchService.search_products(
        query=query,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        available_only=available_only,
        sort_by=clean_sort_by,
        skip=skip,
        limit=limit,
    )

    return SearchResponse(
        total=total,
        query=query,
        applied_filters=applied_filters,
        skip=skip,
        limit=limit,
        products=products,
    )
