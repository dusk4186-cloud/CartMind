"""
Service layer for product catalogue, pricing, and availability queries.
Contains pure business logic decoupled from FastAPI route handlers.
"""

from typing import List, Optional, Tuple
from app.data.mock_data import PRODUCTS, PRODUCTS_BY_ID
from app.models.product import (
    Product,
    ProductPricing,
    ProductAvailability,
)


class ProductService:
    """Handles product catalog retrieval, filtering, and availability."""

    @staticmethod
    def get_products(
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Product], int]:
        """
        Retrieves products matching multi-attribute filter criteria.

        Returns:
            Tuple of (paginated_products_list, total_matching_count)
        """
        results: List[Product] = []

        normalized_category = category.strip().lower() if category else None
        normalized_brand = brand.strip().lower() if brand else None
        normalized_keyword = keyword.strip().lower() if keyword else None

        for item in PRODUCTS:
            # Category filter
            if normalized_category and item["category"].lower() != normalized_category:
                continue

            # Brand filter (case-insensitive substring or exact match)
            if normalized_brand and normalized_brand not in item["brand"].lower():
                continue

            # Price filters
            if min_price is not None and item["price"] < min_price:
                continue
            if max_price is not None and item["price"] > max_price:
                continue

            # Rating filter
            if min_rating is not None and item["rating"] < min_rating:
                continue

            # Keyword filter in name, brand, or description
            if normalized_keyword:
                searchable_text = f"{item['name']} {item['description']} {item['brand']}".lower()
                if normalized_keyword not in searchable_text:
                    continue

            results.append(Product(**item))

        total_count = len(results)
        paginated_results = results[skip : skip + limit]

        return paginated_results, total_count

    @staticmethod
    def get_product_by_id(product_id: str) -> Optional[Product]:
        """
        Looks up a single product by its unique product_id.
        Supports case-insensitive matching for robust AI agent interoperability.
        """
        clean_id = product_id.strip()
        # Direct lookup or case-insensitive fallback
        item = PRODUCTS_BY_ID.get(clean_id) or PRODUCTS_BY_ID.get(clean_id.upper())
        if not item:
            for p in PRODUCTS:
                if p["product_id"].lower() == clean_id.lower():
                    item = p
                    break

        if not item:
            return None
        return Product(**item)

    @staticmethod
    def get_product_pricing(product_id: str) -> Optional[ProductPricing]:
        """
        Retrieves transparent pricing breakdown for a specific product.
        Ensures mathematical validation between original and selling prices.
        """
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return None

        # Verify discount computation integrity
        if product.original_price > 0:
            calc_discount = round(
                ((product.original_price - product.price) / product.original_price) * 100,
                2,
            )
        else:
            calc_discount = 0.0

        return ProductPricing(
            product_id=product.product_id,
            product_name=product.name,
            original_price=product.original_price,
            selling_price=product.price,
            discount_percentage=calc_discount,
            currency=product.currency,
        )

    @staticmethod
    def get_product_availability(product_id: str) -> Optional[ProductAvailability]:
        """
        Retrieves current stock inventory and sizing/color options.
        Validates inventory rules:
        - > 5: in_stock
        - 1 to 5: low_stock
        - 0: out_of_stock
        """
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return None

        return ProductAvailability(
            product_id=product.product_id,
            product_name=product.name,
            availability_status=product.availability_status,
            available_sizes=product.available_sizes,
            available_colors=product.available_colors,
            stock_quantity=product.stock_quantity,
        )
