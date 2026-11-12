"""
Routers package initialization.
"""

from app.routers.products import router as products_router
from app.routers.pricing import router as pricing_router
from app.routers.reviews import router as reviews_router
from app.routers.availability import router as availability_router
from app.routers.search import router as search_router
from app.routers.sentiment import router as sentiment_router
from app.routers.support import router as support_router
from app.routers.feedback import router as feedback_router
from app.routers.agent import router as agent_router

__all__ = [
    "products_router",
    "pricing_router",
    "reviews_router",
    "availability_router",
    "search_router",
    "sentiment_router",
    "support_router",
    "feedback_router",
    "agent_router",
]


