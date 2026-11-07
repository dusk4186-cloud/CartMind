"""
Comprehensive automated tests for Mock E-Commerce API using Pytest and FastAPI TestClient.
Covers all 14 mandatory test requirements plus edge cases.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data.mock_data import PRODUCTS

client = TestClient(app)


# ============================================================================
# 1. Retrieving the complete product catalogue
# ============================================================================
def test_get_complete_product_catalogue():
    """Verify GET /api/products returns all catalogue items with pagination metadata."""
    response = client.get("/api/products?limit=100")
    assert response.status_code == 200
    data = response.json()

    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "products" in data
    assert data["total"] == len(PRODUCTS)
    assert len(data["products"]) == len(PRODUCTS)
    assert data["total"] >= 20  # Requirement: at least 20 products


# ============================================================================
# 2. Filtering products by category
# ============================================================================
@pytest.mark.parametrize("category", ["Belts", "Shoes", "Wallets", "Jackets"])
def test_filter_products_by_category(category):
    """Verify category filtering strictly returns items matching requested category."""
    response = client.get(f"/api/products?category={category}&limit=50")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] > 0
    for product in data["products"]:
        assert product["category"].lower() == category.lower()


# ============================================================================
# 3. Filtering by price range
# ============================================================================
def test_filter_products_by_price_range():
    """Verify min_price and max_price boundaries filter items correctly."""
    min_price = 1000.0
    max_price = 3000.0
    response = client.get(f"/api/products?min_price={min_price}&max_price={max_price}&limit=50")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] > 0
    for product in data["products"]:
        assert min_price <= product["price"] <= max_price


# ============================================================================
# 4. Retrieving a specific product
# ============================================================================
def test_get_specific_product_success():
    """Verify retrieving a valid product by product_id returns complete details."""
    response = client.get("/api/products/PROD001")
    assert response.status_code == 200
    product = response.json()

    assert product["product_id"] == "PROD001"
    assert product["name"] == "Classic Reversible Leather Belt"
    assert product["category"] == "Belts"
    assert product["brand"] == "Wildhorn"
    assert product["price"] == 999.0
    assert product["original_price"] == 1999.0
    assert product["currency"] == "INR"
    assert product["rating"] >= 1.0
    assert product["review_count"] >= 3
    assert product["availability_status"] in ["in_stock", "low_stock", "out_of_stock"]
    assert len(product["available_sizes"]) > 0
    assert len(product["available_colors"]) > 0


# ============================================================================
# 5. Handling nonexistent product IDs
# ============================================================================
def test_get_nonexistent_product_returns_404():
    """Verify GET /api/products/{invalid_id} returns HTTP 404 with descriptive detail."""
    response = client.get("/api/products/PROD999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "PROD999" in data["detail"]


# ============================================================================
# 6. Retrieving pricing information
# ============================================================================
def test_get_product_pricing():
    """Verify pricing endpoint accurately calculates discounts and returns transparent breakdown."""
    response = client.get("/api/products/PROD001/price")
    assert response.status_code == 200
    pricing = response.json()

    assert pricing["product_id"] == "PROD001"
    assert pricing["product_name"] == "Classic Reversible Leather Belt"
    assert pricing["original_price"] == 1999.0
    assert pricing["selling_price"] == 999.0
    assert pricing["currency"] == "INR"
    # (1999 - 999) / 1999 * 100 = 50.025... -> 50.03
    expected_discount = round(((1999.0 - 999.0) / 1999.0) * 100, 2)
    assert abs(pricing["discount_percentage"] - expected_discount) < 0.01


def test_pricing_nonexistent_product_returns_404():
    """Verify pricing endpoint returns 404 for nonexistent product ID."""
    response = client.get("/api/products/PROD_DOES_NOT_EXIST/price")
    assert response.status_code == 404


# ============================================================================
# 7. Retrieving customer reviews
# ============================================================================
def test_get_customer_reviews():
    """Verify customer reviews endpoint returns list with required fields and total count."""
    response = client.get("/api/products/PROD001/reviews")
    assert response.status_code == 200
    data = response.json()

    assert data["product_id"] == "PROD001"
    assert data["total_reviews"] >= 3  # Requirement: at least 3-5 hardcoded reviews
    assert len(data["reviews"]) == data["total_reviews"]

    first_rev = data["reviews"][0]
    required_keys = {
        "review_id",
        "product_id",
        "reviewer_name",
        "rating",
        "comment",
        "review_date",
        "verified_purchase",
    }
    assert required_keys.issubset(first_rev.keys())
    assert 1.0 <= first_rev["rating"] <= 5.0


def test_reviews_nonexistent_product_returns_404():
    """Verify reviews endpoint returns 404 for invalid product ID."""
    response = client.get("/api/products/PROD_INVALID_ID/reviews")
    assert response.status_code == 404


# ============================================================================
# 8. Filtering reviews by rating
# ============================================================================
def test_filter_reviews_by_rating():
    """Verify min_rating query parameter filters product reviews correctly."""
    min_rating = 4.5
    response = client.get(f"/api/products/PROD001/reviews?min_rating={min_rating}")
    assert response.status_code == 200
    data = response.json()

    for rev in data["reviews"]:
        assert rev["rating"] >= min_rating


# ============================================================================
# 9. Checking product availability
# ============================================================================
def test_check_product_availability():
    """Verify availability endpoint returns stock status, sizes, colors, and quantity."""
    response = client.get("/api/products/PROD001/availability")
    assert response.status_code == 200
    avail = response.json()

    assert avail["product_id"] == "PROD001"
    assert avail["product_name"] == "Classic Reversible Leather Belt"
    assert avail["availability_status"] == "in_stock"
    assert avail["stock_quantity"] == 15
    assert len(avail["available_sizes"]) > 0
    assert len(avail["available_colors"]) > 0


def test_availability_nonexistent_product_returns_404():
    """Verify availability endpoint returns 404 for invalid product ID."""
    response = client.get("/api/products/PROD_NOT_FOUND/availability")
    assert response.status_code == 404


# ============================================================================
# 10. Searching products using keywords
# ============================================================================
def test_search_products_by_keyword():
    """Verify smart keyword search matches terms in name, category, or description."""
    response = client.get("/api/search?query=running%20shoes")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] > 0
    # First ranked result should be running shoes
    top_result = data["products"][0]
    searchable_text = f"{top_result['name']} {top_result['description']}".lower()
    assert "running" in searchable_text or "shoes" in searchable_text


def test_search_products_multi_token():
    """Verify search handles multi-word query (comfortable black shoes)."""
    response = client.get("/api/search?query=comfortable%20black%20shoes&max_price=3000&min_rating=4")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] > 0
    for product in data["products"]:
        assert product["price"] <= 3000.0
        assert product["rating"] >= 4.0


# ============================================================================
# 11. Sorting search results by price and rating
# ============================================================================
def test_search_sort_by_price_asc():
    """Verify sorting search results by price ascending."""
    response = client.get("/api/search?sort_by=price_asc&limit=50")
    assert response.status_code == 200
    products = response.json()["products"]
    assert len(products) > 1

    prices = [p["price"] for p in products]
    assert prices == sorted(prices)


def test_search_sort_by_price_desc():
    """Verify sorting search results by price descending."""
    response = client.get("/api/search?sort_by=price_desc&limit=50")
    assert response.status_code == 200
    products = response.json()["products"]
    assert len(products) > 1

    prices = [p["price"] for p in products]
    assert prices == sorted(prices, reverse=True)


def test_search_sort_by_rating_desc():
    """Verify sorting search results by customer rating descending."""
    response = client.get("/api/search?sort_by=rating_desc&limit=50")
    assert response.status_code == 200
    products = response.json()["products"]
    assert len(products) > 1

    ratings = [p["rating"] for p in products]
    assert ratings == sorted(ratings, reverse=True)


# ============================================================================
# 12. Handling empty search results
# ============================================================================
def test_search_empty_results():
    """Verify nonexistent keyword returns HTTP 200 with total=0 and empty products list."""
    response = client.get("/api/search?query=nonexistentunfindablekeywordxyz12345")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert data["products"] == []


# ============================================================================
# 13. Validating invalid price and rating parameters
# ============================================================================
def test_invalid_price_range_catalogue_returns_422():
    """Verify min_price > max_price returns HTTP 422 in catalogue endpoint."""
    response = client.get("/api/products?min_price=5000&max_price=1000")
    assert response.status_code == 422
    assert "min_price cannot be greater than max_price" in response.json()["detail"]


def test_invalid_price_range_search_returns_422():
    """Verify min_price > max_price returns HTTP 422 in search endpoint."""
    response = client.get("/api/search?min_price=5000&max_price=2000")
    assert response.status_code == 422
    assert "min_price cannot be greater than max_price" in response.json()["detail"]


def test_invalid_rating_parameter_returns_422():
    """Verify out-of-bounds rating (>5 or <1) returns HTTP 422 validation error."""
    # min_rating > 5
    response = client.get("/api/products?min_rating=6.5")
    assert response.status_code == 422

    # min_rating < 1
    response = client.get("/api/products?min_rating=0.5")
    assert response.status_code == 422


def test_invalid_sort_by_option_returns_422():
    """Verify invalid sort_by option returns HTTP 422."""
    response = client.get("/api/search?sort_by=invalid_sort_key")
    assert response.status_code == 422
    assert "Invalid sort_by option" in response.json()["detail"]


# ============================================================================
# 14. Verifying stock quantities match availability statuses
# ============================================================================
def test_stock_quantity_matches_availability_status():
    """
    Verify across the entire catalogue that:
    - stock_quantity > 5  => in_stock
    - 1 <= stock_quantity <= 5 => low_stock
    - stock_quantity == 0 => out_of_stock
    """
    response = client.get("/api/products?limit=100")
    assert response.status_code == 200
    products = response.json()["products"]

    in_stock_count = 0
    low_stock_count = 0
    out_of_stock_count = 0

    for p in products:
        qty = p["stock_quantity"]
        status = p["availability_status"]

        if qty > 5:
            assert status == "in_stock", f"Product {p['product_id']} has qty {qty} but status '{status}'"
            in_stock_count += 1
        elif 1 <= qty <= 5:
            assert status == "low_stock", f"Product {p['product_id']} has qty {qty} but status '{status}'"
            low_stock_count += 1
        else:
            assert qty == 0
            assert status == "out_of_stock", f"Product {p['product_id']} has qty {qty} but status '{status}'"
            out_of_stock_count += 1

    # Ensure all 3 statuses are represented in mock catalogue
    assert in_stock_count > 0
    assert low_stock_count > 0
    assert out_of_stock_count > 0


# ============================================================================
# Additional Tests: Pagination, Available Only Filter, Root & Health
# ============================================================================
def test_catalogue_pagination():
    """Verify skip and limit parameters on catalogue endpoint."""
    res1 = client.get("/api/products?skip=0&limit=5")
    assert res1.status_code == 200
    data1 = res1.json()
    assert len(data1["products"]) == 5

    res2 = client.get("/api/products?skip=5&limit=5")
    assert res2.status_code == 200
    data2 = res2.json()
    assert len(data2["products"]) == 5

    # Check non-overlapping
    ids1 = {p["product_id"] for p in data1["products"]}
    ids2 = {p["product_id"] for p in data2["products"]}
    assert ids1.isdisjoint(ids2)


def test_search_available_only_filter():
    """Verify available_only=true excludes out_of_stock products."""
    response = client.get("/api/search?available_only=true&limit=100")
    assert response.status_code == 200
    products = response.json()["products"]

    for p in products:
        assert p["availability_status"] != "out_of_stock"
        assert p["stock_quantity"] > 0


def test_root_and_health_endpoints():
    """Verify root index and health check endpoints."""
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert root_res.json()["name"] == "Mock E-Commerce API for Agentic AI"

    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"


def test_swagger_ui_empty_query_params_handling():
    """Verify Swagger UI blank input fields (empty strings) do not trigger 422 errors."""
    response = client.get("/api/search?query=&category=&brand=&min_price=&max_price=&min_rating=&sort_by=")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(PRODUCTS)

    products_res = client.get("/api/products?category=&brand=&min_price=&max_price=&min_rating=&keyword=")
    assert products_res.status_code == 200
    assert products_res.json()["total"] == len(PRODUCTS)
