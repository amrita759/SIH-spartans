"""
backend/app/services/alert_service.py
Alert lifecycle management and threshold dispatch for high-risk cash-out locations.
"""

import uuid
import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.models import AlertModel, CaseModel
from backend.app.db.repository import AlertRepository, CaseRepository

class AlertService:
    @staticmethod
    def evaluate_and_generate_alerts(
        db: Session,
        case_id: str,
        prediction_id: str,
        ranked_locations: List[Dict[str, Any]]
    ) -> List[AlertModel]:
        """
        Evaluates ranked candidate locations against alert threshold (>= 80.0).
        Generates predictive intelligence alerts for priority intervention.
        """
        generated = []
        for loc in ranked_locations:
            if loc["risk_score"] >= settings.ALERT_RISK_THRESHOLD:
                alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
                
                # Compose actionable LEA message
                msg = (
                    f"HIGH-RISK CASH-OUT LOCATION PREDICTED\n"
                    f"Case: {case_id} | Location: {loc['location_id']} ({loc.get('bank_name', 'Bank')})\n"
                    f"Risk Score: {loc['risk_score']}/100 [{loc['risk_level']}] | Rank: #{loc['rank']}\n"
                    f"Spatial Coordinates: ({loc['latitude']:.4f}, {loc['longitude']:.4f})\n"
                    f"Prediction Window: Next 6 hours. Timely surveillance recommended."
                )

                alert_data = {
                    "alert_id": alert_id,
                    "case_id": case_id,
                    "prediction_id": prediction_id,
                    "location_id": loc["location_id"],
                    "location_name": loc.get("location_name", "ATM"),
                    "bank_name": loc.get("bank_name", "UNKNOWN"),
                    "risk_score": loc["risk_score"],
                    "risk_level": loc["risk_level"],
                    "rank": loc["rank"],
                    "message": msg,
                    "status": "NEW",
                    "created_at": datetime.datetime.now(datetime.timezone.utc)
                }
                alert = AlertRepository.create(db, alert_data)
                generated.append(alert)
                print(f"Generated alert {alert_id} for high-risk location {loc['location_id']} (Risk: {loc['risk_score']})")

        return generated

    @staticmethod
    def get_alerts(db: Session, status: Optional[str] = None) -> List[AlertModel]:
        return AlertRepository.get_all(db, status=status)

    @staticmethod
    def acknowledge_alert(
        db: Session,
        alert_id: str,
        acknowledged_by: str = "LEA_OFFICER"
    ) -> Optional[AlertModel]:
        alert = AlertRepository.acknowledge(db, alert_id, acknowledged_by)
        if alert:
            # Also update case status to UNDER_REVIEW
            case = db.query(CaseModel).filter(CaseModel.case_id == alert.case_id).first()
            if case and case.case_status not in ("RESOLVED", "MONITORED"):
                case.case_status = "UNDER_REVIEW"
                case.updated_at = datetime.datetime.now(datetime.timezone.utc)
                db.commit()
        return alert
