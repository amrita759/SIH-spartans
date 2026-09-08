"""
backend/app/services/prediction_service.py
Core prediction orchestration service.
Binds Case -> Candidate Generation -> Feature Preparation -> ML Model Inference ->
Ranking & Risk Scoring -> SHAP Explanations -> Urgency Evaluation -> DB Persistence -> LEA Alerts.
"""

import uuid
import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.ml.model_adapter import MLModelAdapter
from backend.app.services.feature_service import FeatureService
from backend.app.services.ranking_service import RankingService
from backend.app.services.shap_service import SHAPService
from backend.app.services.alert_service import AlertService
from backend.app.services.location_service import LocationService
from backend.app.db.repository import CaseRepository, PredictionRepository
from backend.app.db.models import CaseModel
from backend.app.schemas.prediction import PredictionRequest, PredictionResponse, RankedLocationItem, ExplanationFactor
from src.risk.urgency import UrgencyTracker

class PredictionService:
    def __init__(
        self,
        model_adapter: Optional[MLModelAdapter] = None,
        ranking_service: Optional[RankingService] = None,
        location_service: Optional[LocationService] = None
    ):
        print("Initializing PredictionService singleton...")
        self.adapter = model_adapter or MLModelAdapter()
        self.ranker = ranking_service or RankingService()
        self.location_service = location_service or LocationService()
        self.urgency_tracker = UrgencyTracker()
        print("PredictionService successfully ready.")

    def run_prediction_for_case(
        self,
        db: Session,
        request: PredictionRequest
    ) -> PredictionResponse:
        """
        Executes end-to-end prediction pipeline for an active cybercrime complaint.
        """
        # 1. Retrieve case from database
        case = CaseRepository.get_by_id(db, request.case_id)
        if not case:
            raise ValueError(f"Case with ID '{request.case_id}' not found in active database.")

        # 2. Parse prediction time T
        pred_time_str = request.prediction_time or case.prediction_time or datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            pred_dt = datetime.datetime.fromisoformat(pred_time_str.replace("Z", "+00:00"))
        except Exception:
            pred_dt = datetime.datetime.now(datetime.timezone.utc)

        case_dict = {
            "case_id": case.case_id,
            "fraud_type": case.fraud_type,
            "fraud_amount": case.fraud_amount,
            "complaint_time": case.complaint_time,
            "prediction_time": pred_time_str,
            "state": case.state,
            "district": case.district,
            "victim_latitude": case.victim_latitude,
            "victim_longitude": case.victim_longitude,
            "last_known_activity": {
                "timestamp": case.last_activity_timestamp,
                "channel": case.last_activity_channel,
                "amount": case.last_activity_amount,
                "recipient_account_id": case.last_activity_recipient,
                "latitude": case.last_activity_latitude,
                "longitude": case.last_activity_longitude
            }
        }

        # 3. Candidate Generation (Spatial proximity + Bank match + Hotspots)
        cand_input = {
            "state": case.state or "MAHARASHTRA",
            "district": case.district or "MUMBAI SUBURBAN",
            "victim_lat": case.victim_latitude or 19.0760,
            "victim_lon": case.victim_longitude or 72.8777,
            "last_known_activity": {
                "latitude": case.last_activity_latitude or case.victim_latitude or 19.0760,
                "longitude": case.last_activity_longitude or case.victim_longitude or 72.8777
            }
        }
        candidates_df = self.location_service.generate_candidates_for_case(cand_input, max_candidates=25)

        # 4. Dynamic Feature Extraction at time T (zero hardcoding)
        features_df, dists_km = FeatureService.build_candidate_features(case_dict, candidates_df, pred_dt)

        # 5. Transform and Model Inference
        X_matrix = self.adapter.transform_input(features_df)
        raw_scores = self.adapter.predict_probability(X_matrix)

        # 6. TreeSHAP Local Explanations
        raw_explanations = self.adapter.explain_prediction(X_matrix, top_factors_count=4)

        # 7. Ranking and Risk Score Calibration
        ranked_items = self.ranker.rank_candidates(
            candidates_df=candidates_df,
            raw_scores=raw_scores,
            dists_km=dists_km,
            top_k=request.top_k
        )

        # 8. Attach SHAP factors to ranked output
        ranked_locations: List[Dict[str, Any]] = []
        pydantic_locations: List[RankedLocationItem] = []

        cand_loc_ids = candidates_df["location_id"].values.astype(str)

        for item in ranked_items:
            match_indices = [idx for idx, lid in enumerate(cand_loc_ids) if lid == item["location_id"]]
            if match_indices:
                factors_raw = raw_explanations[match_indices[0]]
                formatted_factors = SHAPService.format_explanations(factors_raw)
            else:
                formatted_factors = []

            item["top_factors"] = formatted_factors
            ranked_locations.append(item)

            pydantic_factors = [
                ExplanationFactor(
                    feature=f["feature"],
                    contribution=f["contribution"],
                    impact=f["direction"].upper(),
                    description=f["description"]
                )
                for f in formatted_factors
            ]

            pydantic_locations.append(
                RankedLocationItem(
                    rank=item["rank"],
                    location_id=item["location_id"],
                    location_name=item["location_name"],
                    location_type=item["location_type"],
                    bank_name=item["bank_name"],
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                    district=item["district"],
                    state=item["state"],
                    model_score=item["model_score"],
                    risk_score=item["risk_score"],
                    risk_level=item["risk_level"],
                    top_factors=pydantic_factors
                )
            )

        # 9. Time-aware Urgency Evaluation
        urgency_data = self.urgency_tracker.evaluate_urgency(
            prediction_time_iso=pred_time_str,
            window_hours=float(request.prediction_window_hours)
        )
        urgency_level = urgency_data["urgency_level"]
        remaining_hours = urgency_data["remaining_hours"]

        # 10. Store Prediction in Database
        prediction_id = f"PRED-{uuid.uuid4().hex[:8].upper()}"
        highest_risk = ranked_locations[0]["risk_score"] if ranked_locations else 0.0
        highest_level = ranked_locations[0]["risk_level"] if ranked_locations else "LOW"

        PredictionRepository.create(
            db=db,
            prediction_id=prediction_id,
            case_id=request.case_id,
            prediction_time=pred_time_str,
            prediction_window_hours=request.prediction_window_hours,
            model_version=self.adapter.version,
            total_candidates_scored=len(candidates_df),
            highest_risk_score=highest_risk,
            highest_risk_level=highest_level,
            urgency_level=urgency_level,
            remaining_hours=remaining_hours,
            locations=ranked_locations
        )

        # 11. Trigger Alerts for High/Critical Risk Locations
        AlertService.evaluate_and_generate_alerts(
            db=db,
            case_id=request.case_id,
            prediction_id=prediction_id,
            ranked_locations=ranked_locations
        )

        # 12. Update Case Status in Database
        CaseRepository.update_prediction_status(
            db=db,
            case_id=request.case_id,
            status="PREDICTION_READY",
            risk_level=highest_level,
            prediction_id=prediction_id
        )

        return PredictionResponse(
            prediction_id=prediction_id,
            case_id=request.case_id,
            prediction_time=pred_time_str,
            prediction_window_hours=request.prediction_window_hours,
            model_version=self.adapter.version,
            total_candidates_scored=len(candidates_df),
            urgency_level=urgency_level,
            remaining_hours=remaining_hours,
            locations=pydantic_locations
        )

# Global singleton
_pred_service_instance: Optional[PredictionService] = None

def get_prediction_service() -> PredictionService:
    global _pred_service_instance
    if _pred_service_instance is None:
        _pred_service_instance = PredictionService()
    return _pred_service_instance
