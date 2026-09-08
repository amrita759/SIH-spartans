"""
backend/app/schemas/location.py
Pydantic schemas for candidate and master ATM/CRM locations, including multi-case risk locations.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class LocationBase(BaseModel):
    location_id: str
    location_name: Optional[str] = "ATM"
    location_type: str = "ATM"  # ATM, CRM, BRANCH
    bank_name: Optional[str] = "STATE BANK OF INDIA"
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    population_group: Optional[str] = "URBAN"

class LocationResponse(LocationBase):
    id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class RiskLocationOutput(BaseModel):
    location_id: str
    latitude: float
    longitude: float
    risk_score: float
    risk_level: str
    rank: int
    bank: str
    location_type: str
    prediction_id: Optional[str] = None
    prediction_ids: Optional[List[str]] = []
    case_count: Optional[int] = 1
    highest_case_risk: Optional[float] = None
    district: Optional[str] = None
    state: Optional[str] = None

class RiskLocationsResponse(BaseModel):
    status: str = "SUCCESS"
    count: int
    locations: List[RiskLocationOutput]
