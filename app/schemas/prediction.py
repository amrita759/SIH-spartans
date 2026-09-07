import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.prediction import RiskLevel


class PredictionRequest(BaseModel):
    latitude: float
    longitude: float
    time: Optional[datetime] = None
    amount: Optional[float] = 50000.0


class PredictionOut(BaseModel):
    id: uuid.UUID
    latitude: float
    longitude: float
    risk_score: int
    risk_level: RiskLevel
    confidence: float
    predicted_time: datetime
    model_version: str
    prediction_reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)