"""
Service layer for customer reviews retrieval, rating filtering, and pagination.
"""

from typing import List, Optional, Tuple
from app.data.mock_data import REVIEWS
from app.models.product import Review
from app.services.product_service import ProductService


class ReviewService:
    """Handles review querying, rating filters, and validation against product catalog."""

    @staticmethod
    def get_product_reviews(
        product_id: str,
        min_rating: Optional[float] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Optional[Tuple[List[Review], int]]:
        """
        Retrieves reviews for a specified product.

        Returns:
            None if product_id does not exist in catalog.
            Tuple of (paginated_reviews_list, total_matching_count) if product exists.
        """
        # Validate that the product exists first
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return None

        canonical_id = product.product_id

        # Collect reviews matching product
        matching_reviews: List[Review] = []
        for r in REVIEWS:
            if r["product_id"].upper() == canonical_id.upper():
                if min_rating is not None and r["rating"] < min_rating:
                    continue
                matching_reviews.append(Review(**r))

        total_count = len(matching_reviews)
        paginated = matching_reviews[skip : skip + limit]

        return paginated, total_count
