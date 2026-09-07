import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.complaint import ComplaintStatus


class ComplaintCreate(BaseModel):
    complaint_id: str
    crime_category: str
    description: Optional[str] = None
    fraud_amount: float
    complaint_datetime: datetime
    state: str
    district: str
    latitude: float
    longitude: float


class ComplaintUpdate(BaseModel):
    crime_category: Optional[str] = None
    description: Optional[str] = None
    fraud_amount: Optional[float] = None
    status: Optional[ComplaintStatus] = None


class ComplaintOut(BaseModel):
    id: uuid.UUID
    complaint_id: str
    crime_category: str
    description: Optional[str] = None
    fraud_amount: float
    complaint_datetime: datetime
    state: str
    district: str
    latitude: float
    longitude: float
    status: ComplaintStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)