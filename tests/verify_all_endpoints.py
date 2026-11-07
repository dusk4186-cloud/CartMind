"""
Comprehensive HTTP/API verification suite for all mock e-commerce endpoints.
"""

import httpx

BASE_URL = "http://127.0.0.1:8000"


def verify_all():
    client = httpx.Client(base_url=BASE_URL, timeout=5.0)
    print("=====================================================================")
    print("     STARTING COMPREHENSIVE HTTP / API VERIFICATION SUITE            ")
    print("=====================================================================\n")

    passed_checks = 0

    # 1. Health and Root
    r = client.get("/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print(f"[PASS] 1. GET /health -> Status {r.status_code}, data: {r.json()}")
    passed_checks += 1

    r = client.get("/")
    assert r.status_code == 200
    print(f"[PASS] 2. GET / -> Status {r.status_code}, app: {r.json()['name']}")
    passed_checks += 1

    # 2. Product Catalogue
    r = client.get("/api/products?limit=25")
    assert r.status_code == 200
    catalog = r.json()
    assert catalog["total"] == 24
    print(f"[PASS] 3. GET /api/products -> Status 200, Total catalog items: {catalog['total']}")
    passed_checks += 1

    # 3. Category Filter
    for cat in ["Belts", "Shoes", "Wallets", "Jackets"]:
        r = client.get(f"/api/products?category={cat}")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 6
        print(f"[PASS] 4. GET /api/products?category={cat} -> Status 200, Count: {data['total']}")
        passed_checks += 1

    # 4. Product Details
    r = client.get("/api/products/PROD001")
    assert r.status_code == 200
    prod = r.json()
    assert prod["name"] == "Classic Reversible Leather Belt"
    print(f"[PASS] 5. GET /api/products/PROD001 -> Status 200, Item: '{prod['name']}' ({prod['brand']})")
    passed_checks += 1

    # 5. Nonexistent Product (404)
    r = client.get("/api/products/NONEXISTENT_ID")
    assert r.status_code == 404
    print(f"[PASS] 6. GET /api/products/NONEXISTENT_ID -> Status 404, Detail: '{r.json()['detail']}'")
    passed_checks += 1

    # 6. Pricing Breakdown
    r = client.get("/api/products/PROD001/price")
    assert r.status_code == 200
    pricing = r.json()
    assert pricing["selling_price"] == 999.0
    assert pricing["original_price"] == 1999.0
    print(f"[PASS] 7. GET /api/products/PROD001/price -> Status 200, Price: {pricing['selling_price']} INR (Discount: {pricing['discount_percentage']}%)")
    passed_checks += 1

    # 7. Customer Reviews
    r = client.get("/api/products/PROD001/reviews")
    assert r.status_code == 200
    reviews = r.json()
    assert reviews["total_reviews"] >= 3
    print(f"[PASS] 8. GET /api/products/PROD001/reviews -> Status 200, Total Reviews: {reviews['total_reviews']}")
    passed_checks += 1

    # 8. Filter Reviews by Rating
    r = client.get("/api/products/PROD001/reviews?min_rating=4.5")
    assert r.status_code == 200
    for rev in r.json()["reviews"]:
        assert rev["rating"] >= 4.5
    print(f"[PASS] 9. GET /api/products/PROD001/reviews?min_rating=4.5 -> Status 200, High rated reviews: {len(r.json()['reviews'])}")
    passed_checks += 1

    # 9. Product Availability & Stock Check
    r = client.get("/api/products/PROD001/availability")
    assert r.status_code == 200
    avail = r.json()
    assert avail["availability_status"] == "in_stock"
    assert avail["stock_quantity"] == 15
    print(f"[PASS] 10. GET /api/products/PROD001/availability -> Status 200, Status: '{avail['availability_status']}', Qty: {avail['stock_quantity']}")
    passed_checks += 1

    # 10. Smart Product Search (Multi-token)
    r = client.get("/api/search?query=comfortable%20black%20shoes&max_price=3000&min_rating=4")
    assert r.status_code == 200
    search_data = r.json()
    assert search_data["total"] > 0
    print(f"[PASS] 11. GET /api/search?query=comfortable black shoes -> Status 200, Matches found: {search_data['total']}")
    passed_checks += 1

    # 11. Search with Empty Parameters (Swagger UI Try-It-Out behavior)
    r = client.get("/api/search?query=&category=&brand=&min_price=&max_price=&min_rating=&sort_by=")
    assert r.status_code == 200
    assert r.json()["total"] == 24
    print(f"[PASS] 12. GET /api/search (all blank parameters) -> Status 200, Returned all {r.json()['total']} products")
    passed_checks += 1

    # 12. Sorting (Price Ascending)
    r = client.get("/api/search?sort_by=price_asc&limit=10")
    assert r.status_code == 200
    prices = [p["price"] for p in r.json()["products"]]
    assert prices == sorted(prices)
    print(f"[PASS] 13. GET /api/search?sort_by=price_asc -> Status 200, Lowest price first: {prices[0]} INR <= {prices[-1]} INR")
    passed_checks += 1

    # 13. Sorting (Rating Descending)
    r = client.get("/api/search?sort_by=rating_desc&limit=10")
    assert r.status_code == 200
    ratings = [p["rating"] for p in r.json()["products"]]
    assert ratings == sorted(ratings, reverse=True)
    print(f"[PASS] 14. GET /api/search?sort_by=rating_desc -> Status 200, Highest rating first: {ratings[0]} >= {ratings[-1]}")
    passed_checks += 1

    # 14. Validation Error (min_price > max_price)
    r = client.get("/api/search?min_price=5000&max_price=1000")
    assert r.status_code == 422
    print(f"[PASS] 15. GET /api/search?min_price=5000&max_price=1000 -> Status 422 Validation Error: '{r.json()['detail']}'")
    passed_checks += 1

    # 15. Validation Error (invalid sort_by)
    r = client.get("/api/search?sort_by=nonexistent_sort")
    assert r.status_code == 422
    print(f"[PASS] 16. GET /api/search?sort_by=nonexistent_sort -> Status 422 Validation Error: '{r.json()['detail']}'")
    passed_checks += 1

    # 16. Available Only Filter
    r = client.get("/api/search?available_only=true&limit=50")
    assert r.status_code == 200
    for p in r.json()["products"]:
        assert p["availability_status"] != "out_of_stock"
        assert p["stock_quantity"] > 0
    print(f"[PASS] 17. GET /api/search?available_only=true -> Status 200, Excluded all out-of-stock items ({r.json()['total']} items in stock)")
    passed_checks += 1

    print("\n=====================================================================")
    print(f"     ALL {passed_checks}/{passed_checks} VERIFICATION CHECKS PASSED SUCCESSFULLY!       ")
    print("=====================================================================")


if __name__ == "__main__":
    verify_all()
