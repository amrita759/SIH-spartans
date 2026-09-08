"""
backend/app/services/case_service.py
Case management service handling cybercrime complaints and status updates.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.db.models import CaseModel
from backend.app.db.repository import CaseRepository

class CaseService:
    @staticmethod
    def get_cases(db: Session, status: Optional[str] = None, limit: int = 50) -> List[CaseModel]:
        return CaseRepository.get_all(db, status=status, limit=limit)

    @staticmethod
    def get_case(db: Session, case_id: str) -> Optional[CaseModel]:
        return CaseRepository.get_by_id(db, case_id=case_id)

    @staticmethod
    def update_case_prediction(
        db: Session,
        case_id: str,
        risk_level: str,
        prediction_id: str
    ) -> Optional[CaseModel]:
        return CaseRepository.update_prediction_status(
            db=db,
            case_id=case_id,
            status="PREDICTION_READY",
            risk_level=risk_level,
            prediction_id=prediction_id
        )
