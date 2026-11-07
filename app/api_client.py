"""
HTTP client for communicating with the existing FastAPI mock e-commerce backend.
Encapsulates network error handling, connection failures, status code evaluation, and structured JSON parsing.
"""

from typing import Dict, Any, Optional
import httpx
from app.config import AgentConfig


class EcommerceAPIClient:
    """Standardized HTTP client for invoking existing mock e-commerce endpoints."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self.base_url = (base_url or AgentConfig.get_fastapi_base_url()).rstrip("/")
        self.timeout = timeout or AgentConfig.get_timeout_seconds()

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a GET request against the backend with unified error trapping.

        Returns:
            Dictionary containing endpoint data or standardized error metadata.
        """
        # Filter out None values from query parameters
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        url = f"{self.base_url}{path}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=clean_params)

            if response.status_code == 200:
                try:
                    return {"success": True, "data": response.json()}
                except Exception as json_err:
                    return {
                        "success": False,
                        "error_type": "JSON_DECODE_ERROR",
                        "message": f"Failed to parse backend JSON response: {json_err}",
                        "raw_body": response.text[:200],
                    }
            elif response.status_code == 404:
                detail = response.json().get("detail", "Product or resource not found") if response.headers.get("content-type") == "application/json" else response.text
                return {
                    "success": False,
                    "error_type": "NOT_FOUND",
                    "status_code": 404,
                    "message": detail,
                }
            elif response.status_code == 422:
                detail = response.json().get("detail", "Validation error") if response.headers.get("content-type") == "application/json" else response.text
                return {
                    "success": False,
                    "error_type": "VALIDATION_ERROR",
                    "status_code": 422,
                    "message": detail,
                }
            else:
                return {
                    "success": False,
                    "error_type": "HTTP_ERROR",
                    "status_code": response.status_code,
                    "message": f"Backend returned HTTP {response.status_code}: {response.text[:150]}",
                }

        except httpx.ConnectError:
            return {
                "success": False,
                "error_type": "CONNECTION_ERROR",
                "message": (
                    f"Could not connect to FastAPI backend at {self.base_url}. "
                    "Ensure the server is running via 'uvicorn app.main:app --reload'."
                ),
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error_type": "TIMEOUT",
                "message": f"Backend request to {path} timed out after {self.timeout}s.",
            }
        except Exception as e:
            return {
                "success": False,
                "error_type": "UNEXPECTED_ERROR",
                "message": f"Unexpected request failure: {str(e)}",
            }

    def _post(self, path: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a POST request against the backend with unified error trapping.

        Returns:
            Dictionary containing response data or standardized error metadata.
        """
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=json_data)

            if response.status_code in (200, 201):
                try:
                    return {"success": True, "data": response.json()}
                except Exception as json_err:
                    return {
                        "success": False,
                        "error_type": "JSON_DECODE_ERROR",
                        "message": f"Failed to parse backend JSON response: {json_err}",
                        "raw_body": response.text[:200],
                    }
            elif response.status_code == 404:
                detail = response.json().get("detail", "Resource not found") if response.headers.get("content-type") == "application/json" else response.text
                return {
                    "success": False,
                    "error_type": "NOT_FOUND",
                    "status_code": 404,
                    "message": detail,
                }
            elif response.status_code == 422:
                detail = response.json().get("detail", "Validation error") if response.headers.get("content-type") == "application/json" else response.text
                return {
                    "success": False,
                    "error_type": "VALIDATION_ERROR",
                    "status_code": 422,
                    "message": detail,
                }
            else:
                return {
                    "success": False,
                    "error_type": "HTTP_ERROR",
                    "status_code": response.status_code,
                    "message": f"Backend returned HTTP {response.status_code}: {response.text[:150]}",
                }
        except httpx.ConnectError:
            return {
                "success": False,
                "error_type": "CONNECTION_ERROR",
                "message": (
                    f"Could not connect to FastAPI backend at {self.base_url}. "
                    "Ensure the server is running via 'uvicorn app.main:app --reload'."
                ),
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error_type": "TIMEOUT",
                "message": f"Backend request to {path} timed out after {self.timeout}s.",
            }
        except Exception as e:
            return {
                "success": False,
                "error_type": "UNEXPECTED_ERROR",
                "message": f"Unexpected request failure: {str(e)}",
            }

    def search_products(
        self,
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
    ) -> Dict[str, Any]:
        """Calls GET /api/search."""
        params = {
            "query": query,
            "category": category,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price,
            "min_rating": min_rating,
            "available_only": available_only,
            "sort_by": sort_by,
            "skip": skip,
            "limit": limit,
        }
        return self._get("/api/search", params)

    def get_product_catalogue(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Calls GET /api/products."""
        params = {
            "category": category,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price,
            "min_rating": min_rating,
            "keyword": keyword,
            "skip": skip,
            "limit": limit,
        }
        return self._get("/api/products", params)

    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Calls GET /api/products/{product_id}."""
        clean_id = product_id.strip()
        return self._get(f"/api/products/{clean_id}")

    def get_product_pricing(self, product_id: str) -> Dict[str, Any]:
        """Calls GET /api/products/{product_id}/price."""
        clean_id = product_id.strip()
        return self._get(f"/api/products/{clean_id}/price")

    def get_product_reviews(
        self,
        product_id: str,
        min_rating: Optional[float] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Calls GET /api/products/{product_id}/reviews."""
        clean_id = product_id.strip()
        params = {
            "min_rating": min_rating,
            "skip": skip,
            "limit": limit,
        }
        return self._get(f"/api/products/{clean_id}/reviews", params)

    def get_product_availability(self, product_id: str) -> Dict[str, Any]:
        """Calls GET /api/products/{product_id}/availability."""
        clean_id = product_id.strip()
        return self._get(f"/api/products/{clean_id}/availability")

    def get_product_sentiment(self, product_id: str) -> Dict[str, Any]:
        """Calls GET /api/products/{product_id}/sentiment."""
        clean_id = product_id.strip()
        return self._get(f"/api/products/{clean_id}/sentiment")

    def escalate_to_human_support(
        self,
        issue_summary: str,
        category: Optional[str] = "other",
        urgency: Optional[str] = "medium",
        customer_query: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calls POST /api/support/escalate."""
        payload = {
            "issue_summary": issue_summary,
            "category": category or "other",
            "urgency": urgency or "medium",
            "customer_query": customer_query,
            "product_id": product_id,
        }
        return self._post("/api/support/escalate", payload)

    def classify_feedback(self, text: str, review_id: Optional[str] = None) -> Dict[str, Any]:
        """Calls POST /api/feedback/classify."""
        payload = {"text": text, "review_id": review_id}
        return self._post("/api/feedback/classify", payload)

    def get_feedback_samples(self) -> Dict[str, Any]:
        """Calls GET /api/feedback/samples."""
        return self._get("/api/feedback/samples")



