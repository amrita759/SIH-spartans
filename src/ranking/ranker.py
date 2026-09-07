"""
src/ranking/ranker.py
Candidate ranking and risk scoring module.
Converts raw model outputs into calibrated 0-100 risk scores and risk levels (LOW, MEDIUM, HIGH, CRITICAL).
Ranks candidate locations within an active case.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any

class CandidateRanker:
    """
    Ranks candidate locations and assigns calibrated risk scores and levels.
    """
    def __init__(
        self,
        low_thresh: float = 30.0,
        med_thresh: float = 60.0,
        high_thresh: float = 80.0
    ):
        self.low_thresh = low_thresh
        self.med_thresh = med_thresh
        self.high_thresh = high_thresh

    def score_to_risk_level(self, risk_score: float) -> str:
        """Maps 0-100 risk score to operational risk band."""
        if risk_score >= self.high_thresh:
            return "CRITICAL"
        elif risk_score >= self.med_thresh:
            return "HIGH"
        elif risk_score >= self.low_thresh:
            return "MEDIUM"
        else:
            return "LOW"

    def rank_candidates(
        self,
        candidates_df: pd.DataFrame,
        raw_scores: np.ndarray,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Ranks candidates by raw model score and formats API prediction response items.
        """
        df = candidates_df.copy().reset_index(drop=True)
        df["raw_score"] = raw_scores

        # Relative percentile / softmax calibration within candidate set to 0-100
        # High-scoring candidates relative to the pool get scaled to operational risk bands
        s = df["raw_score"].values
        min_s, max_s = np.min(s), np.max(s)
        if max_s > min_s:
            # Scaled score with emphasis on top candidates
            scaled = (s - min_s) / (max_s - min_s)
            # Power scaling to sharpen contrast at the top
            risk_scores = np.round(np.clip(scaled ** 0.8 * 100.0, 0.0, 100.0), 1)
        else:
            risk_scores = np.round(np.clip(s * 100.0, 0.0, 100.0), 1)

        df["risk_score"] = risk_scores
        df["risk_level"] = [self.score_to_risk_level(rs) for rs in risk_scores]

        # Sort descending by risk score
        sorted_df = df.sort_values("risk_score", ascending=False).reset_index(drop=True)
        if top_k:
            sorted_df = sorted_df.head(top_k)

        ranked_results = []
        for rank_idx, row in sorted_df.iterrows():
            item = {
                "rank": rank_idx + 1,
                "location_id": str(row["location_id"]),
                "location_name": str(row.get("location_name", "ATM")),
                "location_type": str(row.get("location_type", "ATM")),
                "bank_name": str(row.get("bank_name", "UNKNOWN")),
                "latitude": float(row["latitude"]) if "latitude" in row else float(row.get("candidate_lat", 0.0)),
                "longitude": float(row["longitude"]) if "longitude" in row else float(row.get("candidate_lon", 0.0)),
                "model_score": round(float(row["raw_score"]), 4),
                "risk_score": float(row["risk_score"]),
                "risk_level": str(row["risk_level"]),
                "district": str(row.get("district", "")),
                "state": str(row.get("state", ""))
            }
            ranked_results.append(item)

        return ranked_results

if __name__ == "__main__":
    # Self-test
    sample_df = pd.DataFrame([
        {"location_id": "ATM001", "location_name": "SBI ATM BKC", "latitude": 19.07, "longitude": 72.87},
        {"location_id": "ATM002", "location_name": "PNB ATM ANDHERI", "latitude": 19.12, "longitude": 72.84},
        {"location_id": "ATM003", "location_name": "BOB ATM DADAR", "latitude": 19.02, "longitude": 72.84}
    ])
    scores = np.array([0.85, 0.42, 0.15])
    ranker = CandidateRanker()
    ranked = ranker.rank_candidates(sample_df, scores, top_k=3)
    print("Ranked test candidates:")
    for r in ranked:
        print(f"Rank {r['rank']}: {r['location_id']} - Score: {r['risk_score']} ({r['risk_level']})")
