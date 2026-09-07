from typing import List, Dict, Any
from pydantic import BaseModel


class HotspotOut(BaseModel):
    cluster_id: int
    latitude: float
    longitude: float
    event_count: int
    risk_score: int
    risk_level: str


class DashboardSummary(BaseModel):
    total_complaints: int
    total_fraud_amount: float
    active_alerts: int
    critical_hotspots: int


class RiskTrend(BaseModel):
    date: str
    complaint_count: int
    predicted_high_risk_events: int