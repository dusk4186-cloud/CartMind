"""
Service layer for smart product search, relevance scoring, and multi-attribute filtering.
Simulates deterministic AI assistant product retrieval without external vector DB dependencies.
"""

from typing import List, Optional, Tuple, Dict, Any
from app.data.mock_data import PRODUCTS
from app.models.product import (
    Product,
    AvailabilityStatus,
    SortByOption,
    SearchFiltersApplied,
)


class SearchService:
    """Provides deterministic smart search and ranking over the product catalog."""

    @staticmethod
    def search_products(
        query: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        available_only: bool = False,
        sort_by: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Product], int, SearchFiltersApplied]:
        """
        Executes smart product search with token-based relevance matching,
        facet filtering, and custom sorting.

        Returns:
            Tuple of (paginated_products, total_matching, applied_filters)
        """
        clean_query = query.strip() if query else None
        query_tokens = [t.lower() for t in clean_query.split()] if clean_query else []

        normalized_category = category.strip().lower() if category else None
        normalized_brand = brand.strip().lower() if brand else None

        scored_candidates: List[Tuple[float, Dict[str, Any]]] = []

        for item in PRODUCTS:
            # 1. Hard filters
            if normalized_category and item["category"].lower() != normalized_category:
                continue

            if normalized_brand and normalized_brand not in item["brand"].lower():
                continue

            if min_price is not None and item["price"] < min_price:
                continue

            if max_price is not None and item["price"] > max_price:
                continue

            if min_rating is not None and item["rating"] < min_rating:
                continue

            if available_only:
                if item["availability_status"] == AvailabilityStatus.OUT_OF_STOCK or item["stock_quantity"] <= 0:
                    continue

            # 2. Relevance calculation if query tokens exist
            if query_tokens:
                score = 0.0
                name_lower = item["name"].lower()
                desc_lower = item["description"].lower()
                cat_lower = item["category"].lower()
                brand_lower = item["brand"].lower()
                colors_lower = " ".join(item.get("available_colors", [])).lower()

                token_matched = False
                for token in query_tokens:
                    token_hit = False
                    if token in name_lower:
                        score += 3.0
                        token_hit = True
                    if token in cat_lower:
                        score += 2.5
                        token_hit = True
                    if token in brand_lower:
                        score += 2.0
                        token_hit = True
                    if token in colors_lower:
                        score += 1.5
                        token_hit = True
                    if token in desc_lower:
                        score += 1.0
                        token_hit = True

                    if token_hit:
                        token_matched = True

                # If query was provided, only keep items with at least one matching token
                if not token_matched:
                    continue

                scored_candidates.append((score, item))
            else:
                scored_candidates.append((1.0, item))

        # 3. Sorting
        normalized_sort = sort_by.strip().lower() if sort_by else None

        if normalized_sort == SortByOption.PRICE_ASC.value:
            scored_candidates.sort(key=lambda x: x[1]["price"])
        elif normalized_sort == SortByOption.PRICE_DESC.value:
            scored_candidates.sort(key=lambda x: x[1]["price"], reverse=True)
        elif normalized_sort == SortByOption.RATING_DESC.value:
            scored_candidates.sort(key=lambda x: x[1]["rating"], reverse=True)
        else:
            # Default sorting: by relevance score descending, then rating descending
            scored_candidates.sort(key=lambda x: (x[0], x[1]["rating"]), reverse=True)

        total_matches = len(scored_candidates)
        paginated_items = [Product(**cand[1]) for cand in scored_candidates[skip : skip + limit]]

        applied_filters = SearchFiltersApplied(
            query=clean_query,
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            available_only=available_only,
            sort_by=sort_by,
        )

        return paginated_items, total_matches, applied_filters
