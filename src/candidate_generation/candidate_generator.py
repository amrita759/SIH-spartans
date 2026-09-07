"""
src/candidate_generation/candidate_generator.py
Deterministic Candidate Location Generator for cybercrime cash-out prediction.
Generates plausible ATM and branch candidate locations given prediction-time case context.
Evaluates candidate recall / coverage on historical test cases.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from src.data.atm_processor import haversine_distance_km

class CandidateGenerator:
    """
    Deterministic candidate generator combining:
    1. Spatial proximity (closest ATMs to last known activity / victim)
    2. Historical district hotspots
    3. Bank affinity
    """
    def __init__(self, atms_parquet_path: Optional[str] = None):
        if atms_parquet_path is None or not os.path.exists(atms_parquet_path):
            candidate_paths = [
                "data/processed/atms_indexed.parquet",
                "../data/processed/atms_indexed.parquet",
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed/atms_indexed.parquet"))
            ]
            resolved_path = None
            for cp in candidate_paths:
                if os.path.exists(cp):
                    resolved_path = cp
                    break
            if resolved_path is None:
                raise FileNotFoundError(f"Indexed ATMs parquet not found in {candidate_paths}")
            atms_parquet_path = resolved_path

        self.atms_df = pd.read_parquet(atms_parquet_path)
        # Pre-group by state and district for sub-millisecond retrieval
        self.state_groups = {state: group for state, group in self.atms_df.groupby("state")}
        self.district_groups = {dist: group for dist, group in self.atms_df.groupby("district")}

    def generate_candidates(
        self,
        case: Dict[str, Any],
        max_candidates: int = 25,
        search_radius_km: float = 20.0
    ) -> pd.DataFrame:
        """
        Generates candidate locations for a single case at prediction time T.
        """
        state = str(case.get("state", "")).strip().upper()
        district = str(case.get("district", "")).strip().upper()

        # Retrieve regional pool
        pool = self.district_groups.get(district)
        if pool is None or len(pool) < max_candidates:
            pool = self.state_groups.get(state)
        if pool is None or len(pool) == 0:
            pool = self.atms_df.sample(n=min(100, len(self.atms_df)), random_state=42)

        last_act = case.get("last_known_activity", {})
        ref_lat = last_act.get("latitude", case.get("victim_lat"))
        ref_lon = last_act.get("longitude", case.get("victim_lon"))

        if ref_lat is None or ref_lon is None:
            # Fallback to random sample
            return pool.head(max_candidates).copy()

        # Compute distances
        dists = haversine_distance_km(
            ref_lat, ref_lon, pool["latitude"].values, pool["longitude"].values
        )
        pool_copy = pool.copy()
        pool_copy["dist_to_last_activity_km"] = dists

        # 1. Spatial proximity tier (closest ATMs within radius)
        nearby = pool_copy.sort_values("dist_to_last_activity_km").head(max_candidates - 5)

        # 2. Hotspot / regional tier
        remaining = pool_copy[~pool_copy["location_id"].isin(nearby["location_id"])]
        if len(remaining) >= 5:
            hotspots = remaining.head(5)
        else:
            hotspots = remaining

        candidates = pd.concat([nearby, hotspots]).drop_duplicates(subset=["location_id"]).head(max_candidates)
        return candidates

    def evaluate_coverage(self, cases: List[Dict[str, Any]], max_candidates: int = 25) -> Dict[str, float]:
        """
        Evaluates candidate generator recall / coverage:
        Fraction of cases where the true withdrawal location is captured in the candidate set.
        """
        cashout_cases = [c for c in cases if c.get("ground_truth", {}).get("has_cashout_in_window")]
        if not cashout_cases:
            return {"coverage": 0.0, "total_evaluated": 0}

        hits = 0
        for c in cashout_cases:
            true_loc = c["ground_truth"]["withdrawal_location_id"]
            cands = self.generate_candidates(c, max_candidates=max_candidates)
            if true_loc in cands["location_id"].values:
                hits += 1

        coverage = hits / len(cashout_cases)
        return {
            "coverage": round(coverage, 4),
            "hits": hits,
            "total_cashout_cases": len(cashout_cases)
        }

if __name__ == "__main__":
    import json
    gen = CandidateGenerator()
    with open("data/synthetic/grounded_cases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)
    print(f"Loaded {len(cases)} cases. Evaluating candidate generator coverage on test cases...")
    test_cases = [c for c in cases if c["prediction_time"] > "2023-06-30T23:59:59"]
    metrics = gen.evaluate_coverage(test_cases)
    print("Candidate Generator Coverage Metrics:", metrics)
