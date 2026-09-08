"""
backend/app/api/routes/locations.py
GIS and ATM/CRM location master queries, including multi-case aggregated map-ready risk points.
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import LocationModel, PredictionLocationModel
from backend.app.schemas.location import LocationResponse, RiskLocationsResponse, RiskLocationOutput
from backend.app.services.location_service import LocationService
from src.risk.scorer import RiskScorer

router = APIRouter(tags=["Locations"])

@router.get("/locations", response_model=List[LocationResponse])
def get_locations(
    state: Optional[str] = Query(default=None, description="Filter by state name"),
    district: Optional[str] = Query(default=None, description="Filter by district name"),
    bank: Optional[str] = Query(default=None, description="Filter by bank name"),
    location_type: Optional[str] = Query(default=None, description="Filter by type (ATM or CRM)"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieves verified ATM and CRM registry locations from master database."""
    service = LocationService()
    return service.get_locations(
        db=db,
        state=state,
        district=district,
        bank=bank,
        location_type=location_type,
        limit=limit
    )

@router.get("/risk-locations", response_model=RiskLocationsResponse)
def get_risk_locations(
    state: Optional[str] = Query(default=None, description="Filter by state"),
    district: Optional[str] = Query(default=None, description="Filter by district"),
    bank: Optional[str] = Query(default=None, description="Filter by bank"),
    risk_level: Optional[str] = Query(default=None, description="Filter by risk band (CRITICAL, HIGH, MEDIUM, LOW)"),
    location_type: Optional[str] = Query(default=None, description="ATM or CRM"),
    prediction_id: Optional[str] = Query(default=None, description="Filter by specific prediction ID"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Returns map-ready high-risk ATM/CRM points for GIS visual intelligence.
    When prediction_id is not specified, aggregates risk across multiple active cases
    using independent risk combination: R_agg(L) = 1 - Prod(1 - R_i(L)).
    """
    query = db.query(PredictionLocationModel)

    if prediction_id:
        query = query.filter(PredictionLocationModel.prediction_id == prediction_id)
        if state:
            query = query.filter(PredictionLocationModel.state == state.upper())
        if district:
            query = query.filter(PredictionLocationModel.district == district.upper())
        if bank:
            query = query.filter(PredictionLocationModel.bank_name.ilike(f"%{bank}%"))
        if risk_level:
            query = query.filter(PredictionLocationModel.risk_level == risk_level.upper())
        if location_type:
            query = query.filter(PredictionLocationModel.location_type == location_type.upper())

        results = query.order_by(PredictionLocationModel.risk_score.desc()).limit(limit).all()

        outputs = [
            RiskLocationOutput(
                location_id=r.location_id,
                latitude=r.latitude,
                longitude=r.longitude,
                risk_score=r.risk_score,
                risk_level=r.risk_level,
                rank=r.rank,
                bank=r.bank_name,
                location_type=r.location_type,
                prediction_id=r.prediction_id,
                prediction_ids=[r.prediction_id],
                case_count=1,
                highest_case_risk=r.risk_score,
                district=r.district,
                state=r.state
            )
            for r in results
        ]
        return RiskLocationsResponse(status="SUCCESS", count=len(outputs), locations=outputs)

    # Multi-Case Aggregation: Retrieve all active prediction locations
    if state:
        query = query.filter(PredictionLocationModel.state == state.upper())
    if district:
        query = query.filter(PredictionLocationModel.district == district.upper())
    if bank:
        query = query.filter(PredictionLocationModel.bank_name.ilike(f"%{bank}%"))
    if location_type:
        query = query.filter(PredictionLocationModel.location_type == location_type.upper())

    all_records = query.all()
    if not all_records:
        return RiskLocationsResponse(status="SUCCESS", count=0, locations=[])

    # Group by location_id and aggregate risk
    scorer = RiskScorer()
    grouped: Dict[str, Dict[str, Any]] = {}
    for r in all_records:
        lid = r.location_id
        if lid not in grouped:
            grouped[lid] = {
                "location_id": lid,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "bank": r.bank_name,
                "location_type": r.location_type,
                "district": r.district,
                "state": r.state,
                "individual_scores": [],
                "prediction_ids": set()
            }
        grouped[lid]["individual_scores"].append(float(r.risk_score))
        grouped[lid]["prediction_ids"].add(r.prediction_id)

    aggregated_list = []
    for lid, item in grouped.items():
        scores = item["individual_scores"]
        # Multi-case independent risk formula: R_agg = 1 - Prod(1 - r/100)
        prob_none = 1.0
        for s in scores:
            prob_none *= (1.0 - min(0.99, s / 100.0))
        r_agg_score = round((1.0 - prob_none) * 100.0, 1)
        r_agg_score = max(r_agg_score, max(scores))  # At least highest single case score
        level = scorer.determine_risk_level(r_agg_score)

        pred_ids = list(item["prediction_ids"])
        aggregated_list.append({
            "location_id": lid,
            "latitude": item["latitude"],
            "longitude": item["longitude"],
            "risk_score": r_agg_score,
            "risk_level": level,
            "bank": item["bank"],
            "location_type": item["location_type"],
            "prediction_id": pred_ids[0] if pred_ids else None,
            "prediction_ids": pred_ids,
            "case_count": len(pred_ids),
            "highest_case_risk": max(scores),
            "district": item["district"],
            "state": item["state"]
        })

    # Filter by risk_level if requested
    if risk_level:
        aggregated_list = [a for a in aggregated_list if a["risk_level"] == risk_level.upper()]

    # Sort descending by aggregated risk_score
    aggregated_list.sort(key=lambda x: x["risk_score"], reverse=True)
    aggregated_list = aggregated_list[:limit]

    outputs = [
        RiskLocationOutput(
            location_id=a["location_id"],
            latitude=a["latitude"],
            longitude=a["longitude"],
            risk_score=a["risk_score"],
            risk_level=a["risk_level"],
            rank=idx + 1,
            bank=a["bank"],
            location_type=a["location_type"],
            prediction_id=a["prediction_id"],
            prediction_ids=a["prediction_ids"],
            case_count=a["case_count"],
            highest_case_risk=a["highest_case_risk"],
            district=a["district"],
            state=a["state"]
        )
        for idx, a in enumerate(aggregated_list)
    ]

    return RiskLocationsResponse(
        status="SUCCESS",
        count=len(outputs),
        locations=outputs
    )
