"""
backend/app/schemas/alert.py
Pydantic schemas for predictive high-risk alerts.
"""

from typing import Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class AlertResponse(BaseModel):
    id: int
    alert_id: str
    case_id: str
    prediction_id: str
    location_id: str
    location_name: Optional[str] = "ATM"
    bank_name: Optional[str] = "UNKNOWN"
    risk_score: float
    risk_level: str
    rank: int = 1
    message: Optional[str] = None
    status: str  # NEW, ACKNOWLEDGED, UNDER_REVIEW, RESOLVED
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[Union[datetime, str]] = None
    created_at: Optional[Union[datetime, str]] = None

    model_config = ConfigDict(from_attributes=True)

class AlertAcknowledgeRequest(BaseModel):
    acknowledged_by: Optional[str] = Field(default="LEA_OFFICER_01", description="Officer ID or callsign")
    notes: Optional[str] = Field(default=None, description="Optional investigative action notes")
