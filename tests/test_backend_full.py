"""
tests/test_backend_full.py
Comprehensive integration test suite verifying all 12 backend endpoints,
LightGBM inference, TreeSHAP explanation, alert dispatch, and DB state transitions.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.repository import init_db

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["model_loaded"] is True
    assert data["model_version"] in ("v1.0.0", "v2.0.0")

def test_model_info_endpoint(client):
    res = client.get("/api/v1/model/info")
    assert res.status_code == 200
    data = res.json()
    assert data["model_name"] == "LightGBM_Cashout_Predictor"
    assert data["total_features"] in (25, 30)
    assert "metrics_summary" in data
    assert "hit_at_10" in data["metrics_summary"]
    assert data["metrics_summary"]["hit_at_10"] > 0.30

def test_cases_endpoint(client):
    res = client.get("/api/v1/cases")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5
    case_ids = [c["case_id"] for c in data]
    assert "CASE-001" in case_ids

def test_single_case_endpoint(client):
    res = client.get("/api/v1/cases/CASE-001")
    assert res.status_code == 200
    data = res.json()
    assert data["case_id"] == "CASE-001"
    assert data["state"] == "MAHARASHTRA"
    assert data["district"] == "MUMBAI SUBURBAN"

def test_predict_and_alert_lifecycle(client):
    # Step 1: Run prediction on CASE-001
    pred_req = {
        "case_id": "CASE-001",
        "prediction_time": "2026-09-08T11:30:00",
        "prediction_window_hours": 6,
        "top_k": 10
    }
    pred_res = client.post("/api/v1/predictions", json=pred_req)
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    
    assert "prediction_id" in pred_data
    pred_id = pred_data["prediction_id"]
    assert pred_data["case_id"] == "CASE-001"
    assert len(pred_data["locations"]) == 10

    # Verify rank order and risk scores
    top1 = pred_data["locations"][0]
    assert top1["rank"] == 1
    assert top1["risk_score"] >= 80.0
    assert top1["risk_level"] in ("CRITICAL", "HIGH")
    assert len(top1["top_factors"]) > 0

    # Step 2: Fetch prediction details
    det_res = client.get(f"/api/v1/predictions/{pred_id}")
    assert det_res.status_code == 200
    det_data = det_res.json()
    assert det_data["prediction_id"] == pred_id
    assert len(det_data["locations"]) == 10

    # Step 3: Fetch SHAP explanation for location
    exp_res = client.get(f"/api/v1/predictions/{pred_id}/explanation?location_id={top1['location_id']}")
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert exp_data["location_id"] == top1["location_id"]
    assert len(exp_data["top_factors"]) > 0
    assert exp_data["top_factors"][0]["direction"] in ("increases_risk", "decreases_risk")

    # Step 4: Verify generated Alert
    alerts_res = client.get("/api/v1/alerts")
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) > 0
    case_alert = [a for a in alerts if a["case_id"] == "CASE-001"]
    assert len(case_alert) > 0
    alert_id = case_alert[0]["alert_id"]

    # Step 5: Acknowledge Alert and verify case status transition
    ack_res = client.post(f"/api/v1/alerts/{alert_id}/acknowledge", json={"acknowledged_by": "OFFICER_PATIL"})
    assert ack_res.status_code == 200
    ack_data = ack_res.json()
    assert ack_data["status"] == "ACKNOWLEDGED"
    assert ack_data["acknowledged_by"] == "OFFICER_PATIL"

    # Step 6: Verify Case status changed to UNDER_REVIEW
    updated_case_res = client.get("/api/v1/cases/CASE-001")
    assert updated_case_res.status_code == 200
    updated_case = updated_case_res.json()
    assert updated_case["case_status"] == "UNDER_REVIEW"
    assert updated_case["prediction_status"] == "COMPLETED"

def test_locations_endpoints(client):
    # Master locations
    loc_res = client.get("/api/v1/locations?limit=10")
    assert loc_res.status_code == 200
    assert len(loc_res.json()) > 0

    # Risk locations for GIS
    risk_res = client.get("/api/v1/risk-locations?limit=20")
    assert risk_res.status_code == 200
    risk_data = risk_res.json()
    assert risk_data["status"] == "SUCCESS"
    assert len(risk_data["locations"]) > 0

def test_analytics_summary_endpoint(client):
    res = client.get("/api/v1/analytics/summary")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert data["kpis"]["total_cases"] >= 5
    assert "risk_distribution" in data
    assert "model_performance" in data
    assert "hit_at_10" in data["model_performance"]
    assert data["model_performance"]["hit_at_10"] > 0.30
