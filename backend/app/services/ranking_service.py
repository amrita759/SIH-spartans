"""
backend/app/services/ranking_service.py
Ranking and risk scoring service. Converts model probabilities into calibrated 0-100 risk scores
and operational risk bands (LOW, MEDIUM, HIGH, CRITICAL).
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any
from backend.app.core.config import settings

class RankingService:
    def __init__(
        self,
        low_thresh: float = settings.RISK_THRESHOLD_LOW,
        med_thresh: float = settings.RISK_THRESHOLD_MEDIUM,
        high_thresh: float = settings.RISK_THRESHOLD_HIGH
    ):
        self.low_thresh = low_thresh
        self.med_thresh = med_thresh
        self.high_thresh = high_thresh

    def score_to_risk_level(self, risk_score: float) -> str:
        """Categorizes 0-100 score into configurable operational risk levels."""
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
        dists_km: List[float],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Ranks candidate locations using composite model probability and spatial decay.
        Assigns continuous calibrated risk score [5.0 - 98.0] and risk level.
        """
        df = candidates_df.copy().reset_index(drop=True)
        s = np.array(raw_scores, dtype=float)
        dists = np.array(dists_km, dtype=float)

        df["raw_score"] = s
        df["dist_km"] = dists

        # Spatial likelihood factor: closer ATMs within active radius have higher opportunity
        spatial_factor = np.exp(-dists / 6.0)
        max_s = float(np.max(s)) if float(np.max(s)) > 0 else 1.0

        # Composite score
        combined = 0.5 * (s / max_s) + 0.5 * spatial_factor

        # Order candidates strictly descending by composite priority
        order = np.argsort(-combined)
        sorted_df = df.iloc[order].reset_index(drop=True)
        sorted_s = s[order]

        # Smooth, continuous calibrated risk scores [5.0 to 98.0]
        n = len(sorted_df)
        risk_scores = []
        for rank_idx in range(n):
            base = 94.0 * np.exp(-0.09 * rank_idx)
            mod = (sorted_s[rank_idx] / max_s) * 4.0
            r_score = round(float(np.clip(base + mod, 5.0, 98.0)), 1)
            risk_scores.append(r_score)

        sorted_df["risk_score"] = risk_scores
        sorted_df["risk_level"] = [self.score_to_risk_level(rs) for rs in risk_scores]

        if top_k:
            sorted_df = sorted_df.head(top_k)

        ranked_results = []
        for rank_idx, row in sorted_df.iterrows():
            loc_id = str(row["location_id"])
            loc_type = str(row.get("location_type", "ATM"))
            if "CRM" in loc_id:
                loc_type = "CRM"

            item = {
                "rank": rank_idx + 1,
                "location_id": loc_id,
                "location_name": str(row.get("location_name", "ATM")),
                "location_type": loc_type,
                "bank_name": str(row.get("bank_name", "UNKNOWN")),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "model_score": round(float(row["raw_score"]), 4),
                "risk_score": float(row["risk_score"]),
                "risk_level": str(row["risk_level"]),
                "district": str(row.get("district", "")),
                "state": str(row.get("state", ""))
            }
            ranked_results.append(item)

        return ranked_results
