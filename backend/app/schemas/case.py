"""
backend/app/schemas/case.py
Pydantic schemas for cybercrime cases and complaint management.
"""

from typing import Optional, Union, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class LastKnownActivity(BaseModel):
    timestamp: str = Field(..., description="Timestamp of last activity (<= prediction_time)")
    channel: str = Field(default="UPI", description="Payment channel: UPI, RTGS, IMPS, Net_Banking, Mobile_App")
    amount: float = Field(..., gt=0.0, description="Amount transferred in latest step")
    recipient_account_id: Optional[str] = Field(default=None, description="Anonymized/tokenized mule account ID")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Geographic latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Geographic longitude")

class CaseBase(BaseModel):
    case_id: str = Field(..., description="Unique cybercrime case ID")
    fraud_type: str = Field(default="investment_scam", description="Cybercrime modus operandi")
    fraud_amount: float = Field(..., gt=0.0, description="Total complaint amount in INR")
    complaint_time: Optional[str] = Field(default=None, description="Complaint timestamp")
    prediction_time: Optional[str] = Field(default=None, description="Prediction snapshot time T")
    prediction_window_hours: int = Field(default=6, description="Prediction window in hours (default: 6)")
    state: Optional[str] = Field(default="MAHARASHTRA", description="State name")
    district: Optional[str] = Field(default=None, description="District name")
    victim_latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    victim_longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0)

class CaseCreate(CaseBase):
    last_known_activity: Optional[LastKnownActivity] = None

class CaseResponse(CaseBase):
    id: int
    case_status: str = Field(..., description="NEW, ANALYZING, PREDICTION_READY, UNDER_REVIEW, MONITORED, RESOLVED")
    prediction_status: str = Field(..., description="PENDING or COMPLETED")
    latest_prediction_id: Optional[str] = None
    risk_level: Optional[str] = None
    last_activity_channel: Optional[str] = None
    last_activity_amount: Optional[float] = None
    last_activity_latitude: Optional[float] = None
    last_activity_longitude: Optional[float] = None
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None

    model_config = ConfigDict(from_attributes=True)

class PatrolDispatchRequest(BaseModel):
    patrol_unit: str = Field(default="PCR-DELTA-04", description="Patrol team callsign or police station unit")
    target_location_id: str = Field(..., description="Candidate ATM/CRM location ID targeted for surveillance")
    directives: Optional[str] = Field(default=None, description="Tactical directives given to patrol unit")

class PatrolDispatchResponse(BaseModel):
    status: str
    message: str
    case: CaseResponse
    dispatched_unit: str
    target_location_id: str
    dispatch_timestamp: str
