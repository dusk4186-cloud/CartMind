"""
API router for product catalogue browsing and detailed product view.
Designed for high AI agent tool discoverability and deterministic outputs.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.product import Product, ProductListResponse, ErrorResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get(
    "",
    response_model=ProductListResponse,
    summary="Retrieve Product Catalogue",
    description=(
        "Fetch products from the e-commerce catalogue with optional filtering by category, "
        "brand, price boundaries, minimum rating, and text keyword. Returns paginated results."
    ),
    responses={
        status.HTTP_200_OK: {"description": "List of matching products with pagination metadata"},
        422: {"model": ErrorResponse, "description": "Invalid query parameters"},
    },
)
def get_products(
    category: Optional[str] = Query(
        None,
        description="Filter products by category name (e.g., 'Belts', 'Shoes', 'Wallets', 'Jackets')",
    ),
    brand: Optional[str] = Query(
        None,
        description="Filter products by brand name (e.g., 'Woodland', 'Bata', 'Nike')",
    ),
    min_price: Optional[float] = Query(
        None,
        ge=0,
        description="Minimum product price in INR (e.g., 1000.0)",
    ),
    max_price: Optional[float] = Query(
        None,
        ge=0,
        description="Maximum product price in INR (e.g., 5000.0)",
    ),
    min_rating: Optional[float] = Query(
        None,
        ge=1.0,
        le=5.0,
        description="Minimum average customer rating 1.0 to 5.0 (e.g., 4.0)",
    ),
    keyword: Optional[str] = Query(
        None,
        description="Search keyword to match against product name or description (e.g., 'leather')",
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
) -> ProductListResponse:
    """Retrieve catalog products with comprehensive filtering and pagination."""
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=422,
            detail="min_price cannot be greater than max_price",
        )

    products, total = ProductService.get_products(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )

    return ProductListResponse(
        total=total,
        skip=skip,
        limit=limit,
        products=products,
    )


@router.get(
    "/{product_id}",
    response_model=Product,
    summary="Get Product Details by ID",
    description="Retrieve comprehensive details for a single product specified by its unique product_id.",
    responses={
        status.HTTP_200_OK: {"description": "Complete product details found"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Product not found"},
    },
)
def get_product_by_id(product_id: str) -> Product:
    """Retrieve complete product information by unique ID."""
    product = ProductService.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )
    return product
