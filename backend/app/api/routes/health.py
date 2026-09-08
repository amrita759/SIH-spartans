"""
backend/app/api/routes/health.py
Health check route for SIH26184 backend services.
"""

import datetime
from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def get_health():
    """Returns runtime health status and version information."""
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "model_loaded": True,
        "model_version": settings.MODEL_VERSION,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
