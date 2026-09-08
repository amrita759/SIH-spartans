"""
backend/app/core/config.py
Configuration settings for SIH26184 Predictive Location Intelligence API.
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SIH26184 Predictive Cash-Withdrawal Location Intelligence"
    PROJECT_DESCRIPTION: str = (
        "Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely "
        "Cash Withdrawal Locations in Advance. Ministry of Home Affairs - I4C / SIH 2026."
    )
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # ML Artifacts Paths
    ARTIFACTS_DIR: str = os.getenv("ARTIFACTS_DIR", "artifacts")
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "v2.0.0")
    ATMS_PARQUET_PATH: str = os.getenv(
        "ATMS_PARQUET_PATH", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/processed/atms_indexed.parquet"))
    )
    
    # Operational Risk Thresholds
    ALERT_RISK_THRESHOLD: float = float(os.getenv("ALERT_RISK_THRESHOLD", "80.0"))
    RISK_THRESHOLD_LOW: float = 30.0
    RISK_THRESHOLD_MEDIUM: float = 60.0
    RISK_THRESHOLD_HIGH: float = 80.0
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sih26184.db")
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Prediction defaults
    DEFAULT_TOP_K: int = 10
    MAX_TOP_K: int = 50
    DEFAULT_PREDICTION_WINDOW_HOURS: int = 6

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
