import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    title: str
    summary: str
    latitude: float
    longitude: float
    risk_level: str
    risk_score: int
    predicted_locations: List[Dict[str, Any]]
    related_complaints: List[str]
    related_transactions: List[str]
    recommended_action: str


class ReportOut(BaseModel):
    id: uuid.UUID
    title: str
    summary: str
    risk_level: str
    risk_score: int
    latitude: float
    longitude: float
    predicted_locations: List[Dict[str, Any]]
    related_complaints: List[str]
    related_transactions: List[str]
    recommended_action: str
    created_by: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)