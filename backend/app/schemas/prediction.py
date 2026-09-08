"""
backend/app/schemas/prediction.py
Pydantic schemas for predictive cash-withdrawal scoring, ranking, SHAP explanations,
outcome logging, and complaint NLP intake.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ExplanationFactor(BaseModel):
    feature: str
    contribution: float
    impact: str  # INCREASES_RISK, DECREASES_RISK
    description: str

class RankedLocationItem(BaseModel):
    rank: int
    location_id: str
    location_name: Optional[str] = "ATM"
    location_type: str = "ATM"  # ATM or CRM
    bank_name: Optional[str] = "UNKNOWN"
    latitude: float
    longitude: float
    district: Optional[str] = ""
    state: Optional[str] = ""
    model_score: float
    risk_score: float
    risk_level: str
    top_factors: List[ExplanationFactor] = []

class PredictionRequest(BaseModel):
    case_id: str = Field(..., description="Unique cybercrime case ID (e.g. CASE-001)")
    prediction_time: Optional[str] = Field(default=None, description="ISO timestamp snapshot T")
    prediction_window_hours: int = Field(default=6, description="Prediction window in hours (default: 6)")
    top_k: int = Field(default=10, ge=1, le=50, description="Top K candidate locations to rank")

class PredictionResponse(BaseModel):
    prediction_id: str
    case_id: str
    prediction_time: str
    prediction_window_hours: int
    model_version: str
    total_candidates_scored: int
    urgency_level: Optional[str] = "NORMAL"
    remaining_hours: Optional[float] = 6.0
    locations: List[RankedLocationItem]

class ExplanationFactorItem(BaseModel):
    feature: str
    impact: float
    direction: str
    description: str

class LocationExplanationResponse(BaseModel):
    prediction_id: str
    location_id: str
    risk_score: float
    risk_level: str
    top_factors: List[ExplanationFactorItem]

class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    prediction_horizon_hours: int
    feature_count: int
    feature_names: List[str]
    created_at: str
    metrics_summary: Dict[str, Any]
    benchmarks: Optional[Dict[str, Any]] = None

class OutcomeCreate(BaseModel):
    case_id: str = Field(..., description="Case identifier")
    prediction_id: str = Field(..., description="Prediction identifier")
    actual_location_id: str = Field(..., description="Real ATM/CRM location ID where cashout occurred")
    actual_withdrawal_time: Optional[str] = Field(default=None, description="ISO timestamp of actual withdrawal")
    withdrawal_occurred: bool = Field(default=True, description="Whether fraudulent cashout actually materialized")
    apprehended: bool = Field(default=False, description="Whether suspect/mule was intercepted")
    notes: Optional[str] = Field(default=None, description="Investigator notes")

class OutcomeResponse(BaseModel):
    status: str = "SUCCESS"
    message: str = "Outcome recorded for evaluation."
    outcome_id: str
    case_id: str
    prediction_id: str
    actual_location_id: str
    rank_of_actual: Optional[int] = None
    in_top_3: bool = False
    in_top_5: bool = False
    in_top_10: bool = False
    lead_time_hours: Optional[float] = None
    prediction_risk_score: Optional[float] = None

class ComplaintParseRequest(BaseModel):
    complaint_text: str = Field(..., description="Raw cybercrime complaint narrative text")

class ComplaintParseResponse(BaseModel):
    raw_text: str
    fraud_amount: Optional[float] = None
    fraud_type: str = "upi_phishing"
    channel: str = "UPI"
    state: Optional[str] = "MAHARASHTRA"
    district: Optional[str] = None
    bank: Optional[str] = None
    transaction_keywords: List[str] = []
    incident_time: Optional[str] = None
    review_status: str = "PENDING_CONFIRMATION"
