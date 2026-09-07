"""
tests/test_ranking.py
Verifies ranking logic, risk score bounds [0, 100], and risk band mapping.
"""

import pytest
import numpy as np
import pandas as pd
from src.ranking.ranker import CandidateRanker

def test_ranking_and_risk_scores():
    ranker = CandidateRanker()
    sample_df = pd.DataFrame([
        {"location_id": "L1", "latitude": 19.0, "longitude": 72.0},
        {"location_id": "L2", "latitude": 19.1, "longitude": 72.1},
        {"location_id": "L3", "latitude": 19.2, "longitude": 72.2},
    ])
    scores = np.array([0.9, 0.4, 0.1])
    ranked = ranker.rank_candidates(sample_df, scores, top_k=3)

    assert len(ranked) == 3
    assert ranked[0]["location_id"] == "L1"
    assert ranked[0]["rank"] == 1
    assert ranked[0]["risk_level"] == "CRITICAL"
    assert 0.0 <= ranked[0]["risk_score"] <= 100.0
    assert 0.0 <= ranked[2]["risk_score"] <= 100.0
    assert ranked[0]["risk_score"] >= ranked[1]["risk_score"] >= ranked[2]["risk_score"]
