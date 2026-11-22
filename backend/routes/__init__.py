"""
API Routes Package for Land Shield AI.
"""

from backend.routes.health import router as health_router
from backend.routes.predict import router as predict_router

__all__ = ["health_router", "predict_router"]
