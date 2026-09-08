"""
backend/app/api/routes/model_info.py
Model information and validation metrics endpoints.
"""

from fastapi import APIRouter, Depends
from backend.app.services.prediction_service import get_prediction_service, PredictionService

router = APIRouter(prefix="/model", tags=["Model Information"])

@router.get("/info")
def get_model_info(service: PredictionService = Depends(get_prediction_service)):
    """
    Returns verified model architecture specifications, feature contracts, and out-of-time evaluation metrics.
    No synthetic metrics are fabricated.
    """
    return service.adapter.get_model_info()
