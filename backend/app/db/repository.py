"""
backend/app/db/repository.py
Repository layer for SQLite database operations, seeding demo cases, fetching records,
and tracking closed-loop intervention outcomes.
"""

import os
import json
import uuid
import datetime
import pandas as pd
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from backend.app.db.database import engine, Base, SessionLocal
from backend.app.db.models import (
    CaseModel, PredictionModel, PredictionLocationModel,
    AlertModel, LocationModel, OutcomeModel
)

def init_db():
    """Initializes tables and seeds initial demo cases and locations."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data_if_empty(db)
    finally:
        db.close()

def seed_data_if_empty(db: Session):
    """Seeds demo cases and master locations if tables are empty."""
    # Seed Demo Cases from demo_cases.json
    if db.query(CaseModel).count() == 0:
        demo_cases_path = os.path.join(os.path.dirname(__file__), "../data/demo_cases.json")
        if os.path.exists(demo_cases_path):
            with open(demo_cases_path, "r", encoding="utf-8") as f:
                cases_data = json.load(f)
            for c in cases_data:
                last_act = c.get("last_known_activity") or {}
                case = CaseModel(
                    case_id=c["case_id"],
                    case_status=c.get("case_status", "NEW"),
                    fraud_type=c.get("fraud_type", "investment_scam"),
                    fraud_amount=c.get("fraud_amount", 0.0),
                    complaint_time=c.get("complaint_time"),
                    prediction_time=c.get("prediction_time"),
                    prediction_window_hours=c.get("prediction_window_hours", 6),
                    state=c.get("state", "MAHARASHTRA"),
                    district=c.get("district", "MUMBAI SUBURBAN"),
                    victim_latitude=c.get("victim_latitude"),
                    victim_longitude=c.get("victim_longitude"),
                    last_activity_timestamp=last_act.get("timestamp") or c.get("last_activity_timestamp"),
                    last_activity_channel=last_act.get("channel") or c.get("last_activity_channel", "UPI"),
                    last_activity_amount=last_act.get("amount") or c.get("last_activity_amount", 0.0),
                    last_activity_recipient=last_act.get("recipient_account_id") or c.get("last_activity_recipient"),
                    last_activity_latitude=last_act.get("latitude") or c.get("last_activity_latitude"),
                    last_activity_longitude=last_act.get("longitude") or c.get("last_activity_longitude"),
                    prediction_status=c.get("prediction_status", "PENDING"),
                    risk_level=c.get("risk_level"),
                )
                db.add(case)
            db.commit()
            print(f"Seeded {len(cases_data)} demo cases into database.")

    # Seed Locations Master Sample
    if db.query(LocationModel).count() == 0:
        loc_csv = os.path.join(os.path.dirname(__file__), "../data/locations_master.csv")
        if os.path.exists(loc_csv):
            df_sample = pd.read_csv(loc_csv).head(2000)
            for _, row in df_sample.iterrows():
                loc = LocationModel(
                    location_id=str(row["location_id"]),
                    location_name=str(row.get("location_name", "ATM")),
                    location_type=str(row.get("location_type", "ATM")),
                    bank_name=str(row.get("bank_name", "STATE BANK OF INDIA")),
                    state=str(row.get("state", "")),
                    district=str(row.get("district", "")),
                    pincode=str(row.get("pincode", "")),
                    population_group=str(row.get("population_group", "URBAN")),
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"])
                )
                db.add(loc)
            db.commit()
            print(f"Seeded 2000 sample master locations into database.")

class CaseRepository:
    @staticmethod
    def get_all(db: Session, status: Optional[str] = None, limit: int = 50) -> List[CaseModel]:
        query = db.query(CaseModel)
        if status:
            query = query.filter(CaseModel.case_status == status)
        return query.order_by(desc(CaseModel.created_at)).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, case_id: str) -> Optional[CaseModel]:
        return db.query(CaseModel).filter(CaseModel.case_id == case_id).first()

    @staticmethod
    def create(db: Session, case_data: Dict[str, Any]) -> CaseModel:
        case = CaseModel(**case_data)
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def update_prediction_status(
        db: Session,
        case_id: str,
        status: str,
        risk_level: str,
        prediction_id: str
    ):
        case = db.query(CaseModel).filter(CaseModel.case_id == case_id).first()
        if case:
            case.prediction_status = "COMPLETED"
            case.case_status = status
            case.risk_level = risk_level
            case.latest_prediction_id = prediction_id
            case.updated_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()
            db.refresh(case)
        return case

class PredictionRepository:
    @staticmethod
    def create(
        db: Session,
        prediction_id: str,
        case_id: str,
        prediction_time: str,
        prediction_window_hours: int,
        model_version: str,
        total_candidates_scored: int,
        highest_risk_score: float,
        highest_risk_level: str,
        urgency_level: str,
        remaining_hours: float,
        locations: List[Dict[str, Any]]
    ) -> PredictionModel:
        pred = PredictionModel(
            prediction_id=prediction_id,
            case_id=case_id,
            prediction_time=prediction_time,
            prediction_window_hours=prediction_window_hours,
            model_version=model_version,
            total_candidates_scored=total_candidates_scored,
            highest_risk_score=highest_risk_score,
            highest_risk_level=highest_risk_level,
            urgency_level=urgency_level,
            remaining_hours=remaining_hours
        )
        db.add(pred)

        for loc in locations:
            pl = PredictionLocationModel(
                prediction_id=prediction_id,
                rank=loc["rank"],
                location_id=loc["location_id"],
                location_name=loc.get("location_name", "ATM"),
                location_type=loc.get("location_type", "ATM"),
                bank_name=loc.get("bank_name", "UNKNOWN"),
                latitude=loc["latitude"],
                longitude=loc["longitude"],
                district=loc.get("district", ""),
                state=loc.get("state", ""),
                model_score=loc.get("model_score", 0.0),
                risk_score=loc.get("risk_score", 0.0),
                risk_level=loc.get("risk_level", "LOW"),
                top_factors_json=json.dumps(loc.get("top_factors", []))
            )
            db.add(pl)

        db.commit()
        db.refresh(pred)
        return pred

    @staticmethod
    def get_by_id(db: Session, prediction_id: str) -> Optional[PredictionModel]:
        return db.query(PredictionModel).filter(PredictionModel.prediction_id == prediction_id).first()

    @staticmethod
    def get_locations(db: Session, prediction_id: str) -> List[PredictionLocationModel]:
        return db.query(PredictionLocationModel)\
                 .filter(PredictionLocationModel.prediction_id == prediction_id)\
                 .order_by(PredictionLocationModel.rank)\
                 .all()

class AlertRepository:
    @staticmethod
    def get_all(db: Session, status: Optional[str] = None, limit: int = 50) -> List[AlertModel]:
        query = db.query(AlertModel)
        if status:
            query = query.filter(AlertModel.status == status)
        return query.order_by(desc(AlertModel.created_at)).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, alert_id: str) -> Optional[AlertModel]:
        return db.query(AlertModel).filter(AlertModel.alert_id == alert_id).first()

    @staticmethod
    def create(db: Session, alert_data: Dict[str, Any]) -> AlertModel:
        alert = AlertModel(**alert_data)
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def acknowledge(db: Session, alert_id: str, acknowledged_by: str) -> Optional[AlertModel]:
        alert = db.query(AlertModel).filter(AlertModel.alert_id == alert_id).first()
        if alert:
            alert.status = "ACKNOWLEDGED"
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()
            db.refresh(alert)
        return alert

class LocationRepository:
    @staticmethod
    def get_all(
        db: Session,
        state: Optional[str] = None,
        district: Optional[str] = None,
        bank: Optional[str] = None,
        location_type: Optional[str] = None,
        limit: int = 100
    ) -> List[LocationModel]:
        query = db.query(LocationModel)
        if state:
            query = query.filter(LocationModel.state == state.upper())
        if district:
            query = query.filter(LocationModel.district == district.upper())
        if bank:
            query = query.filter(LocationModel.bank_name.ilike(f"%{bank}%"))
        if location_type:
            query = query.filter(LocationModel.location_type == location_type.upper())
        return query.limit(limit).all()

class OutcomeRepository:
    @staticmethod
    def record_outcome(db: Session, outcome_data: Dict[str, Any]) -> OutcomeModel:
        outcome_id = f"OUT_{uuid.uuid4().hex[:10]}"
        outcome = OutcomeModel(
            outcome_id=outcome_id,
            case_id=outcome_data["case_id"],
            prediction_id=outcome_data["prediction_id"],
            actual_location_id=outcome_data["actual_location_id"],
            actual_withdrawal_time=outcome_data.get("actual_withdrawal_time"),
            withdrawal_occurred=outcome_data.get("withdrawal_occurred", True),
            apprehended=outcome_data.get("apprehended", False),
            rank_of_actual=outcome_data.get("rank_of_actual"),
            in_top_3=outcome_data.get("in_top_3", False),
            in_top_5=outcome_data.get("in_top_5", False),
            in_top_10=outcome_data.get("in_top_10", False),
            lead_time_hours=outcome_data.get("lead_time_hours"),
            prediction_risk_score=outcome_data.get("prediction_risk_score"),
            notes=outcome_data.get("notes")
        )
        db.add(outcome)
        db.commit()
        db.refresh(outcome)
        return outcome

    @staticmethod
    def get_all(db: Session, limit: int = 100) -> List[OutcomeModel]:
        return db.query(OutcomeModel).order_by(desc(OutcomeModel.created_at)).limit(limit).all()
