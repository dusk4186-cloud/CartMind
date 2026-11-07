"""
API router for product pricing and discount analysis.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.product import ProductPricing, ErrorResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["Pricing"])


@router.get(
    "/{product_id}/price",
    response_model=ProductPricing,
    summary="Get Product Pricing",
    description=(
        "Retrieve transparent pricing structure for a product, including original price, "
        "selling price, calculated discount percentage, and currency."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Product pricing information retrieved"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Product not found"},
    },
)
def get_product_pricing(product_id: str) -> ProductPricing:
    """Retrieve pricing and discount breakdown for a specific product."""
    pricing = ProductService.get_product_pricing(product_id)
    if not pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )
    return pricing
