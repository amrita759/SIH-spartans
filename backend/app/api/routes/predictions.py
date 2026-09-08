"""
backend/app/api/routes/predictions.py
Prediction inference, SHAP explainability, and closed-loop outcome tracking endpoints.
"""

import json
import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.repository import PredictionRepository, OutcomeRepository, CaseRepository
from backend.app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    LocationExplanationResponse,
    ExplanationFactorItem,
    OutcomeCreate,
    OutcomeResponse
)
from backend.app.services.prediction_service import get_prediction_service, PredictionService

router = APIRouter(tags=["Predictions"])

@router.post("/predictions", response_model=PredictionResponse)
@router.post("/predict", response_model=PredictionResponse)
def create_prediction(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    service: PredictionService = Depends(get_prediction_service)
):
    """
    Executes proactive cash-withdrawal location prediction for an active cybercrime complaint.
    1. Validates case_id.
    2. Builds dynamic prediction-time case state at time T.
    3. Retrieves candidate ATM/CRM locations.
    4. Extracts dynamic feature vectors (zero leakage).
    5. Calls trained LightGBM model.
    6. Ranks candidates and calibrates 0-100 risk score.
    7. Computes TreeSHAP explainability factors.
    8. Dispatches alerts for high-risk scores (>= 80).
    9. Persists and returns Top-K results.
    """
    try:
        response = service.run_prediction_for_case(db=db, request=request)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction pipeline failure: {str(e)}"
        )

@router.get("/predictions/{prediction_id}")
def get_prediction(prediction_id: str, db: Session = Depends(get_db)):
    """Retrieves prediction metadata and scored candidate locations."""
    pred = PredictionRepository.get_by_id(db, prediction_id)
    if not pred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID '{prediction_id}' not found."
        )
    locations = PredictionRepository.get_locations(db, prediction_id)
    loc_items = []
    for loc in locations:
        factors = []
        if loc.top_factors_json:
            try:
                factors = json.loads(loc.top_factors_json)
            except Exception:
                factors = []
        loc_items.append({
            "rank": loc.rank,
            "location_id": loc.location_id,
            "location_name": loc.location_name,
            "location_type": loc.location_type,
            "bank_name": loc.bank_name,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "district": loc.district,
            "state": loc.state,
            "model_score": loc.model_score,
            "risk_score": loc.risk_score,
            "risk_level": loc.risk_level,
            "top_factors": factors
        })

    return {
        "prediction_id": pred.prediction_id,
        "case_id": pred.case_id,
        "prediction_time": pred.prediction_time,
        "prediction_window_hours": pred.prediction_window_hours,
        "model_version": pred.model_version,
        "total_candidates_scored": pred.total_candidates_scored,
        "highest_risk_score": pred.highest_risk_score,
        "highest_risk_level": pred.highest_risk_level,
        "urgency_level": getattr(pred, "urgency_level", "NORMAL"),
        "remaining_hours": getattr(pred, "remaining_hours", 6.0),
        "locations": loc_items
    }

@router.get("/predictions/{prediction_id}/explanation", response_model=LocationExplanationResponse)
def get_prediction_explanation(
    prediction_id: str,
    location_id: Optional[str] = Query(default=None, description="Specific location ID to explain"),
    db: Session = Depends(get_db)
):
    """Retrieves local TreeSHAP factor explanations for a specific predicted ATM/CRM."""
    locations = PredictionRepository.get_locations(db, prediction_id)
    if not locations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No scored candidates found for prediction ID '{prediction_id}'."
        )

    target_loc = locations[0]
    if location_id:
        match = [loc for loc in locations if loc.location_id == location_id]
        if match:
            target_loc = match[0]

    factors = []
    if target_loc.top_factors_json:
        try:
            factors_data = json.loads(target_loc.top_factors_json)
            factors = [
                ExplanationFactorItem(
                    feature=f["feature"],
                    impact=f["contribution"],
                    direction=f["direction"],
                    description=f["description"]
                )
                for f in factors_data
            ]
        except Exception:
            factors = []

    return LocationExplanationResponse(
        prediction_id=prediction_id,
        location_id=target_loc.location_id,
        risk_score=target_loc.risk_score,
        risk_level=target_loc.risk_level,
        top_factors=factors
    )

@router.post("/outcome", response_model=OutcomeResponse)
@router.post("/predictions/outcome", response_model=OutcomeResponse)
@router.post("/feedback", response_model=OutcomeResponse)
def record_outcome(payload: OutcomeCreate, db: Session = Depends(get_db)):
    """
    Closed-loop operational outcome recording endpoint.
    Records actual intervention results, calculates retrospective ranking accuracy,
    and stages data for future scheduled retraining.
    Returns 'Outcome recorded for evaluation.' without asserting premature model accuracy claims.
    """
    locations = PredictionRepository.get_locations(db, payload.prediction_id)
    rank_of_actual = None
    pred_risk = None
    for loc in locations:
        if loc.location_id == payload.actual_location_id:
            rank_of_actual = loc.rank
            pred_risk = loc.risk_score
            break

    in_top_3 = rank_of_actual is not None and rank_of_actual <= 3
    in_top_5 = rank_of_actual is not None and rank_of_actual <= 5
    in_top_10 = rank_of_actual is not None and rank_of_actual <= 10

    # Calculate actual lead time
    pred = PredictionRepository.get_by_id(db, payload.prediction_id)
    lead_time_hours = None
    if pred and payload.actual_withdrawal_time:
        try:
            p_dt = datetime.datetime.fromisoformat(pred.prediction_time.replace("Z", "+00:00"))
            w_dt = datetime.datetime.fromisoformat(payload.actual_withdrawal_time.replace("Z", "+00:00"))
            lead_time_hours = round((w_dt - p_dt).total_seconds() / 3600.0, 2)
        except Exception:
            pass

    outcome_data = {
        "case_id": payload.case_id,
        "prediction_id": payload.prediction_id,
        "actual_location_id": payload.actual_location_id,
        "actual_withdrawal_time": payload.actual_withdrawal_time,
        "withdrawal_occurred": payload.withdrawal_occurred,
        "apprehended": payload.apprehended,
        "rank_of_actual": rank_of_actual,
        "in_top_3": in_top_3,
        "in_top_5": in_top_5,
        "in_top_10": in_top_10,
        "lead_time_hours": lead_time_hours,
        "prediction_risk_score": pred_risk,
        "notes": payload.notes
    }

    recorded = OutcomeRepository.record_outcome(db, outcome_data)

    # Conclude closed-loop workflow: resolve case and alerts
    if payload.case_id:
        case = CaseRepository.get_by_id(db, payload.case_id)
        if case:
            case.case_status = "RESOLVED"
            case.updated_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()

        from backend.app.db.models import AlertModel
        alerts = db.query(AlertModel).filter(AlertModel.case_id == payload.case_id).all()
        for alt in alerts:
            alt.status = "RESOLVED"
        db.commit()

    return OutcomeResponse(
        status="SUCCESS",
        message="Outcome recorded for evaluation.",
        outcome_id=recorded.outcome_id,
        case_id=recorded.case_id,
        prediction_id=recorded.prediction_id,
        actual_location_id=recorded.actual_location_id,
        rank_of_actual=recorded.rank_of_actual,
        in_top_3=recorded.in_top_3,
        in_top_5=recorded.in_top_5,
        in_top_10=recorded.in_top_10,
        lead_time_hours=recorded.lead_time_hours,
        prediction_risk_score=recorded.prediction_risk_score
    )
