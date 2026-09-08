"""
backend/app/db/models.py
SQLAlchemy ORM models for cases, predictions, candidate locations, alerts, master locations, and outcomes.
"""

import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from backend.app.db.database import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class CaseModel(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(64), unique=True, index=True, nullable=False)
    case_status = Column(String(32), default="NEW", index=True)  # NEW, ANALYZING, PREDICTION_READY, UNDER_REVIEW, MONITORED, RESOLVED
    fraud_type = Column(String(64), nullable=False, default="investment_scam")
    fraud_amount = Column(Float, nullable=False, default=0.0)
    complaint_time = Column(String(64), nullable=True)
    prediction_time = Column(String(64), nullable=True)
    prediction_window_hours = Column(Integer, default=6)
    
    state = Column(String(64), default="MAHARASHTRA")
    district = Column(String(64), default="MUMBAI SUBURBAN")
    victim_latitude = Column(Float, nullable=True)
    victim_longitude = Column(Float, nullable=True)
    
    last_activity_timestamp = Column(String(64), nullable=True)
    last_activity_channel = Column(String(32), default="UPI")
    last_activity_amount = Column(Float, default=0.0)
    last_activity_recipient = Column(String(64), nullable=True)
    last_activity_latitude = Column(Float, nullable=True)
    last_activity_longitude = Column(Float, nullable=True)
    
    prediction_status = Column(String(32), default="PENDING")  # PENDING, COMPLETED
    latest_prediction_id = Column(String(64), nullable=True)
    risk_level = Column(String(32), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class PredictionModel(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(64), unique=True, index=True, nullable=False)
    case_id = Column(String(64), index=True, nullable=False)
    prediction_time = Column(String(64), nullable=False)
    prediction_window_hours = Column(Integer, default=6)
    model_version = Column(String(32), default="v2.0.0")
    total_candidates_scored = Column(Integer, default=0)
    highest_risk_score = Column(Float, default=0.0)
    highest_risk_level = Column(String(32), default="LOW")
    urgency_level = Column(String(32), default="NORMAL")
    remaining_hours = Column(Float, default=6.0)
    created_at = Column(DateTime, default=utc_now)

class PredictionLocationModel(Base):
    __tablename__ = "prediction_locations"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(64), index=True, nullable=False)
    rank = Column(Integer, nullable=False)
    location_id = Column(String(64), index=True, nullable=False)
    location_name = Column(String(128), default="ATM")
    location_type = Column(String(32), default="ATM")
    bank_name = Column(String(128), default="UNKNOWN")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    district = Column(String(64), default="")
    state = Column(String(64), default="")
    model_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(32), default="LOW")
    top_factors_json = Column(Text, default="[]")

class AlertModel(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(64), unique=True, index=True, nullable=False)
    case_id = Column(String(64), index=True, nullable=False)
    prediction_id = Column(String(64), index=True, nullable=False)
    location_id = Column(String(64), index=True, nullable=False)
    location_name = Column(String(128), default="ATM")
    bank_name = Column(String(128), default="UNKNOWN")
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(32), default="CRITICAL")
    rank = Column(Integer, default=1)
    message = Column(Text, nullable=True)
    status = Column(String(32), default="NEW", index=True)  # NEW, ACKNOWLEDGED, UNDER_REVIEW, RESOLVED
    acknowledged_by = Column(String(64), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

class LocationModel(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String(64), unique=True, index=True, nullable=False)
    location_name = Column(String(128), default="ATM")
    location_type = Column(String(32), default="ATM")
    bank_name = Column(String(128), default="UNKNOWN")
    state = Column(String(64), index=True, default="")
    district = Column(String(64), index=True, default="")
    pincode = Column(String(32), nullable=True)
    population_group = Column(String(32), default="URBAN")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

class OutcomeModel(Base):
    __tablename__ = "outcomes"

    id = Column(Integer, primary_key=True, index=True)
    outcome_id = Column(String(64), unique=True, index=True, nullable=False)
    case_id = Column(String(64), index=True, nullable=False)
    prediction_id = Column(String(64), index=True, nullable=False)
    actual_location_id = Column(String(64), nullable=False)
    actual_withdrawal_time = Column(String(64), nullable=True)
    withdrawal_occurred = Column(Boolean, default=True)
    apprehended = Column(Boolean, default=False)
    rank_of_actual = Column(Integer, nullable=True)
    in_top_3 = Column(Boolean, default=False)
    in_top_5 = Column(Boolean, default=False)
    in_top_10 = Column(Boolean, default=False)
    lead_time_hours = Column(Float, nullable=True)
    prediction_risk_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
