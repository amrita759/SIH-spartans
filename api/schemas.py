"""
api/schemas.py
Pydantic schemas for the SIH26184 Predictive Cash-Withdrawal Location Intelligence Service.
Strict input validation, frontend-ready output formats, and privacy-preserving field definitions.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import datetime

class LastKnownActivityInput(BaseModel):
    timestamp: str = Field(..., description="ISO 8601 timestamp of last observed account/transfer activity (<= prediction_time)")
    channel: str = Field(default="UPI", description="Channel of transaction, e.g. UPI, IMPS, NEFT, Net_Banking, Mobile_App")
    amount: float = Field(..., gt=0.0, description="Amount in INR involved in the latest activity")
    recipient_account_id: Optional[str] = Field(default=None, description="Anonymized/tokenized identifier of recipient mule account")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude of last activity")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude of last activity")

class CandidateLocationInput(BaseModel):
    location_id: str = Field(..., description="Unique ATM or Branch code (e.g. RBI Part 1 code)")
    location_name: Optional[str] = Field(default="ATM", description="Location or branch title")
    location_type: str = Field(default="ATM", description="ATM or BRANCH")
    bank_name: Optional[str] = Field(default="STATE BANK OF INDIA", description="Operating bank")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate")
    district: Optional[str] = Field(default=None, description="District name")
    state: Optional[str] = Field(default=None, description="State name")
    pincode: Optional[str] = Field(default=None, description="6-digit Indian PIN code")

class PredictRequest(BaseModel):
    case_id: str = Field(..., description="Unique cybercrime case / complaint identifier (e.g. CF2026_00123)")
    prediction_time: str = Field(..., description="Prediction snapshot time T in ISO 8601 format")
    prediction_window_hours: int = Field(default=6, description="Prediction horizon in hours (default: 6)")
    complaint_time: Optional[str] = Field(default=None, description="Timestamp when complaint was registered")
    fraud_type: str = Field(default="investment_scam", description="Cybercrime modus operandi category")
    fraud_amount: float = Field(..., gt=0.0, description="Total disputed / reported complaint amount in INR")
    state: Optional[str] = Field(default="MAHARASHTRA", description="Primary state")
    district: Optional[str] = Field(default=None, description="Primary district")
    victim_latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0, description="Victim geographic latitude")
    victim_longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0, description="Victim geographic longitude")
    last_known_activity: Optional[LastKnownActivityInput] = Field(default=None, description="Most recent known activity snapshot")
    candidate_locations: Optional[List[CandidateLocationInput]] = Field(
        default=None,
        description="Optional list of candidate locations to score. If omitted, candidates are generated automatically."
    )

    @field_validator("prediction_window_hours")
    def validate_window(cls, v):
        if v not in (6, 12, 24):
            raise ValueError("Supported prediction horizons are 6, 12, or 24 hours.")
        return v

class ExplanationFactor(BaseModel):
    feature: str
    contribution: float
    impact: str
    description: str

class RankedLocationOutput(BaseModel):
    rank: int
    location_id: str
    location_name: str
    location_type: str
    bank_name: str
    latitude: float
    longitude: float
    district: str
    state: str
    model_score: float
    risk_score: float
    risk_level: str
    top_factors: List[ExplanationFactor]

class PredictResponse(BaseModel):
    case_id: str
    prediction_time: str
    prediction_window_hours: int
    model_version: str
    total_candidates_scored: int
    predictions: List[RankedLocationOutput]

class HealthResponse(BaseModel):
    status: str
    service: str
    model_loaded: bool
    model_version: str
    timestamp: str

class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    prediction_horizon_hours: int
    supported_windows: List[int]
    total_features: int
    feature_names: List[str]
    created_at: str
    metrics_summary: Dict[str, Any]
