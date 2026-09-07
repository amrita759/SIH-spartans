"""
tests/test_candidate_gen.py
Verifies candidate generator output and geographic constraints.
"""

import pytest
import pandas as pd
from src.candidate_generation.candidate_generator import CandidateGenerator

def test_candidate_generation():
    gen = CandidateGenerator()
    sample_case = {
        "state": "MAHARASHTRA",
        "district": "MUMBAI SUBURBAN",
        "victim_lat": 19.0760,
        "victim_lon": 72.8777,
        "last_known_activity": {
            "latitude": 19.0820,
            "longitude": 72.8850
        }
    }
    cands = gen.generate_candidates(sample_case, max_candidates=20)
    assert len(cands) == 20
    assert "location_id" in cands.columns
    assert "latitude" in cands.columns
    assert "longitude" in cands.columns
    assert (cands["latitude"] > 0).all()
    assert (cands["longitude"] > 0).all()
