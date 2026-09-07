"""
api/routes/prediction.py
Prediction and intelligence delivery endpoints for law enforcement and banking dashboards.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from api.schemas import PredictRequest, PredictResponse
from api.services.prediction_service import get_prediction_service, PredictionService

router = APIRouter(tags=["Prediction"])

@router.post("/predict", response_model=PredictResponse)
def predict_cashout_locations(
    request: PredictRequest,
    top_k: int = Query(default=10, ge=1, le=50, description="Number of top-ranked candidates to return"),
    service: PredictionService = Depends(get_prediction_service)
):
    """
    Predicts likely fraudulent cash-withdrawal locations for an active cybercrime case.
    Accepts only information known at prediction time T.
    Returns ranked candidate ATMs/branches with calibrated risk scores, risk bands, and SHAP explanations.
    """
    try:
        response = service.predict_case(request, top_k=top_k)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference error during candidate risk prediction: {str(e)}"
        )

@router.get("/risk-locations")
def get_risk_locations(
    state: str = Query(default="MAHARASHTRA", description="State filter"),
    limit: int = Query(default=10, ge=1, le=50),
    service: PredictionService = Depends(get_prediction_service)
):
    """
    Returns high-risk active cash-out surveillance zones for GIS heatmap visualization.
    """
    # Sample simulated active monitored cases for dashboard view
    dummy_req = PredictRequest(
        case_id="CF_SURVEILLANCE_ACTIVE",
        prediction_time="2026-09-07T14:30:00",
        prediction_window_hours=6,
        fraud_type="investment_scam",
        fraud_amount=250000.0,
        state=state,
        district="MUMBAI SUBURBAN" if state == "MAHARASHTRA" else "BENGALURU URBAN"
    )
    res = service.predict_case(dummy_req, top_k=limit)
    return {
        "status": "SUCCESS",
        "state": state,
        "monitored_window_hours": 6,
        "critical_count": sum(1 for p in res.predictions if p.risk_level == "CRITICAL"),
        "high_count": sum(1 for p in res.predictions if p.risk_level == "HIGH"),
        "locations": res.predictions
    }
