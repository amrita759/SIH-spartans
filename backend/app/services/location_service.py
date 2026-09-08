"""
backend/app/services/location_service.py
Spatial candidate query and GIS master location retrieval service.
"""

from typing import List, Optional, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.db.models import LocationModel
from backend.app.db.repository import LocationRepository
from src.candidate_generation.candidate_generator import CandidateGenerator

class LocationService:
    def __init__(self, candidate_gen: Optional[CandidateGenerator] = None):
        self.candidate_gen = candidate_gen or CandidateGenerator()

    def generate_candidates_for_case(
        self,
        case_dict: Dict[str, Any],
        max_candidates: int = 25
    ) -> pd.DataFrame:
        """Invokes deterministic candidate generator to retrieve candidate ATM/CRMs."""
        return self.candidate_gen.generate_candidates(case_dict, max_candidates=max_candidates)

    def get_locations(
        self,
        db: Session,
        state: Optional[str] = None,
        district: Optional[str] = None,
        bank: Optional[str] = None,
        location_type: Optional[str] = None,
        limit: int = 100
    ) -> List[LocationModel]:
        return LocationRepository.get_all(
            db=db,
            state=state,
            district=district,
            bank=bank,
            location_type=location_type,
            limit=limit
        )
