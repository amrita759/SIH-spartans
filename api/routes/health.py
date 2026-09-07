"""
api/routes/health.py
Health and status check endpoints.
"""

import datetime
from fastapi import APIRouter, Depends
from api.schemas import HealthResponse
from api.services.prediction_service import get_prediction_service, PredictionService

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def health_check(service: PredictionService = Depends(get_prediction_service)):
    """
    Returns API health status, model load status, and current server time.
    """
    return HealthResponse(
        status="HEALTHY",
        service="SIH26184_Cashout_Location_Prediction_Service",
        model_loaded=service.model is not None,
        model_version=service.version,
        timestamp=datetime.datetime.now().isoformat()
    )
