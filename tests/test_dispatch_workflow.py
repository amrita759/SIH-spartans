import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_patrol_dispatch_and_outcome_lifecycle():
    # 1. Fetch cases
    res = client.get("/api/v1/cases")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) > 0
    case_id = cases[0]["case_id"]

    # 2. Dispatch patrol
    dispatch_payload = {
        "patrol_unit": "PCR-DELTA-04",
        "target_location_id": "00010ATM00002ID1",
        "directives": "Establish plainclothes surveillance at target ATM booth."
    }
    d_res = client.post(f"/api/v1/cases/{case_id}/dispatch", json=dispatch_payload)
    assert d_res.status_code == 200
    assert d_res.json()["status"] == "SUCCESS"
    assert d_res.json()["case"]["case_status"] == "MONITORED"

    # 3. Verify case status is updated to MONITORED
    c_res = client.get(f"/api/v1/cases/{case_id}")
    assert c_res.json()["case_status"] == "MONITORED"

    # 4. Record outcome with 'Ground verification done by patrol team'
    outcome_payload = {
        "case_id": case_id,
        "prediction_id": "PRED-TEST-123",
        "actual_location_id": "00010ATM00002ID1",
        "withdrawal_occurred": True,
        "apprehended": True,
        "notes": "Ground verification done by patrol team. Mule intercepted at ATM booth."
    }
    o_res = client.post("/api/v1/predictions/outcome", json=outcome_payload)
    assert o_res.status_code == 200
    assert o_res.json()["status"] == "SUCCESS"

    # 5. Verify case is now RESOLVED
    c_resolved = client.get(f"/api/v1/cases/{case_id}")
    assert c_resolved.json()["case_status"] == "RESOLVED"