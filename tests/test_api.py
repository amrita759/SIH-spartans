"""
tests/test_api.py
FastAPI integration tests verifying endpoints, Pydantic validation, and response contracts.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["model_loaded"] is True
    assert data["model_version"] == "v1.0.0"

def test_model_info_endpoint():
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_version"] == "v1.0.0"
    assert "feature_names" in data
    assert len(data["feature_names"]) > 0
    assert 6 in data["supported_windows"]

def test_predict_endpoint():
    payload = {
        "case_id": "CF2026_TEST_API_001",
        "prediction_time": "2026-09-07T14:30:00",
        "prediction_window_hours": 6,
        "fraud_type": "investment_scam",
        "fraud_amount": 100000.0,
        "state": "MAHARASHTRA",
        "district": "MUMBAI SUBURBAN",
        "victim_latitude": 19.0760,
        "victim_longitude": 72.8777,
        "last_known_activity": {
            "timestamp": "2026-09-07T14:15:00",
            "channel": "UPI",
            "amount": 50000.0,
            "latitude": 19.0820,
            "longitude": 72.8850
        }
    }
    response = client.post("/predict?top_k=5", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "CF2026_TEST_API_001"
    assert len(data["predictions"]) == 5
    assert data["predictions"][0]["rank"] == 1
    assert "risk_score" in data["predictions"][0]
    assert "risk_level" in data["predictions"][0]
    assert len(data["predictions"][0]["top_factors"]) > 0

def test_risk_locations_endpoint():
    response = client.get("/risk-locations?state=MAHARASHTRA&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "locations" in data
    assert len(data["locations"]) == 5
