from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.ml.prediction import ml_engine
from app.schemas.prediction import PredictionRequest, PredictionOut
from app.schemas.common import APIResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ml", tags=["Machine Learning Engine"])


@router.post("/predict", response_model=APIResponse[PredictionOut])
async def predict_risk(
    payload: PredictionRequest,
    current_user: User = Depends(get_current_user)
):
    target_time = payload.time or datetime.now(timezone.utc)
    res = ml_engine.predict(
        latitude=payload.latitude,
        longitude=payload.longitude,
        target_time=target_time,
        amount=payload.amount or 50000.0
    )
    return APIResponse(message="Risk prediction generated", data=res)


@router.get("/status", response_model=APIResponse[dict])
async def model_status(current_user: User = Depends(get_current_user)):
    return APIResponse(data={
        "active_model": "GradientBoostingClassifier",
        "version": "v1.0.0",
        "is_loaded": ml_engine.model is not None,
        "supported_features": ["latitude", "longitude", "amount", "hour", "dayofweek", "is_night_time"]
    })