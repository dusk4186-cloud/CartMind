"""
API router for product inventory availability and variant stock check.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.product import ProductAvailability, ErrorResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["Availability"])


@router.get(
    "/{product_id}/availability",
    response_model=ProductAvailability,
    summary="Check Product Availability",
    description=(
        "Check stock status, available sizes, available colors, and units remaining for a product. "
        "Categorizes availability as 'in_stock' (>5), 'low_stock' (1-5), or 'out_of_stock' (0)."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Product availability details returned"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Product not found"},
    },
)
def get_product_availability(product_id: str) -> ProductAvailability:
    """Retrieve inventory stock availability and variant options."""
    availability = ProductService.get_product_availability(product_id)
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )
    return availability
