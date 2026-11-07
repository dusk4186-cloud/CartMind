"""
Pydantic data models for the mock e-commerce catalog, pricing, reviews,
availability, and search responses.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class AvailabilityStatus(str, Enum):
    """Enumeration representing product inventory availability status."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


class ProductCategory(str, Enum):
    """Allowed primary product categories."""
    BELTS = "Belts"
    SHOES = "Shoes"
    WALLETS = "Wallets"
    JACKETS = "Jackets"


class SortByOption(str, Enum):
    """Allowed sorting criteria for product search."""
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    RATING_DESC = "rating_desc"


class Product(BaseModel):
    """Comprehensive product model representing a catalogue item."""
    product_id: str = Field(
        ...,
        description="Unique product identifier (e.g., PROD001)",
        examples=["PROD001"],
    )
    name: str = Field(
        ...,
        description="Full commercial name of the product",
        examples=["Classic Reversible Leather Belt"],
    )
    category: str = Field(
        ...,
        description="Product category (Belts, Shoes, Wallets, Jackets)",
        examples=["Belts"],
    )
    brand: str = Field(
        ...,
        description="Brand manufacturer name",
        examples=["Wildhorn"],
    )
    description: str = Field(
        ...,
        description="Detailed product narrative, materials, and highlights",
        examples=["Premium top-grain reversible leather belt with zinc buckle."],
    )
    price: float = Field(
        ...,
        gt=0,
        description="Current selling price in INR",
        examples=[999.0],
    )
    original_price: float = Field(
        ...,
        gt=0,
        description="Original regular price before discount in INR",
        examples=[1999.0],
    )
    discount_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Discount percentage off original price",
        examples=[50.03],
    )
    currency: str = Field(
        default="INR",
        description="Three-letter currency code (INR)",
        examples=["INR"],
    )
    available_sizes: List[str] = Field(
        default_factory=list,
        description="List of currently available sizes (e.g., S, M, L or shoe sizes)",
        examples=[["32", "34", "36", "38"]],
    )
    available_colors: List[str] = Field(
        default_factory=list,
        description="List of available color options",
        examples=[["Black", "Dark Brown"]],
    )
    rating: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Average customer review rating (scale 1.0 to 5.0)",
        examples=[4.5],
    )
    review_count: int = Field(
        ...,
        ge=0,
        description="Total count of customer reviews submitted",
        examples=[4],
    )
    availability_status: AvailabilityStatus = Field(
        ...,
        description="Current stock classification: in_stock, low_stock, or out_of_stock",
        examples=[AvailabilityStatus.IN_STOCK],
    )
    stock_quantity: int = Field(
        ...,
        ge=0,
        description="Exact quantity available in stock",
        examples=[15],
    )


class ProductListResponse(BaseModel):
    """Structured paginated response for product catalogue retrieval."""
    total: int = Field(..., description="Total matching products in catalogue")
    skip: int = Field(..., description="Number of skipped items (pagination offset)")
    limit: int = Field(..., description="Maximum items requested in current page")
    products: List[Product] = Field(..., description="List of matching products")


class ProductPricing(BaseModel):
    """Product pricing and discount breakdown model."""
    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Full commercial product name")
    original_price: float = Field(..., description="Original price before discount")
    selling_price: float = Field(..., description="Current active selling price")
    discount_percentage: float = Field(..., description="Calculated discount percentage")
    currency: str = Field(default="INR", description="Currency code")


class Review(BaseModel):
    """Customer product review model."""
    review_id: str = Field(
        ...,
        description="Unique review identifier (e.g., REV001)",
        examples=["REV001"],
    )
    product_id: str = Field(
        ...,
        description="Associated product identifier",
        examples=["PROD001"],
    )
    reviewer_name: str = Field(
        ...,
        description="Name of the customer who wrote the review",
        examples=["Aarav Sharma"],
    )
    rating: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Rating awarded by reviewer (1 to 5)",
        examples=[5.0],
    )
    comment: str = Field(
        ...,
        description="Reviewer commentary and feedback",
        examples=["Exceptional quality leather and very smooth buckle finish."],
    )
    review_date: str = Field(
        ...,
        description="Date of review in ISO format YYYY-MM-DD",
        examples=["2024-02-14"],
    )
    verified_purchase: bool = Field(
        ...,
        description="True if customer verified purchase from store",
        examples=[True],
    )


class ReviewListResponse(BaseModel):
    """Structured response for customer reviews with pagination."""
    product_id: str = Field(..., description="Associated product identifier")
    total_reviews: int = Field(..., description="Total matching reviews found")
    skip: int = Field(..., description="Number of reviews skipped")
    limit: int = Field(..., description="Maximum reviews requested")
    reviews: List[Review] = Field(..., description="List of review objects")


class ProductAvailability(BaseModel):
    """Product stock inventory status response."""
    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Product name")
    availability_status: AvailabilityStatus = Field(
        ...,
        description="Stock classification: in_stock (>5), low_stock (1-5), out_of_stock (0)",
    )
    available_sizes: List[str] = Field(..., description="List of available sizes")
    available_colors: List[str] = Field(..., description="List of available colors")
    stock_quantity: int = Field(..., ge=0, description="Available inventory units")


class SearchFiltersApplied(BaseModel):
    """Metadata describing all search parameters applied."""
    query: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    available_only: bool = False
    sort_by: Optional[str] = None


class SearchResponse(BaseModel):
    """Structured response for smart product search queries."""
    total: int = Field(..., description="Total number of matching products")
    query: Optional[str] = Field(None, description="Search query string executed")
    applied_filters: SearchFiltersApplied = Field(
        ...,
        description="Summary of all filters and bounds applied",
    )
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination page size limit")
    products: List[Product] = Field(..., description="Ranked list of matching products")


class ErrorResponse(BaseModel):
    """Standardized API error message container."""
    detail: str = Field(..., description="Explanatory human-readable error description")
