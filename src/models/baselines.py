"""
src/models/baselines.py
Progressive baseline models for cash-out location risk prediction:
1. Baseline 0: Historical Hotspot / Frequency heuristic
2. Baseline 1: Spatial Proximity heuristic (inverse distance to last activity)
3. Baseline 2: Regularized Logistic Regression (linear baseline)
4. Baseline 3: Random Forest classifier (tree ensemble baseline)
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from src.features.feature_pipeline import FeaturePipeline
from src.evaluation.metrics import evaluate_model_performance

class HotspotBaseline:
    """Ranks candidates purely by historical fraud count and hour affinity."""
    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        counts = df["hist_atm_fraud_count_90d"].values.astype(float)
        affinity = df["hist_atm_hour_affinity"].values.astype(float)
        scores = counts * 2.0 + affinity
        # Min-max normalize per case
        probs = []
        for case_id, group in df.groupby("case_id", sort=False):
            s = group["hist_atm_fraud_count_90d"].values * 2.0 + group["hist_atm_hour_affinity"].values
            max_s = np.max(s)
            min_s = np.min(s)
            if max_s > min_s:
                norm = (s - min_s) / (max_s - min_s)
            else:
                norm = np.ones_like(s) * 0.04
            probs.extend(norm)
        return np.array(probs)

class SpatialProximityBaseline:
    """Ranks candidates by inverse distance to last known activity."""
    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        dist = df["dist_last_activity_to_candidate_km"].values.astype(float)
        inv_dist = 1.0 / (dist + 0.1)
        # Normalize per case
        probs = []
        for case_id, group in df.groupby("case_id", sort=False):
            d = group["dist_last_activity_to_candidate_km"].values
            inv = 1.0 / (d + 0.1)
            probs.extend(inv / np.sum(inv))
        return np.array(probs)

def run_all_baselines(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    pipeline: FeaturePipeline
) -> Dict[str, Dict[str, Any]]:
    """Runs and evaluates all 4 baseline models on held-out test data."""
    y_train = train_df["target"].values
    y_test = test_df["target"].values
    results = {}

    # 1. Hotspot Heuristic
    hotspot_model = HotspotBaseline()
    hotspot_scores = hotspot_model.predict_proba(test_df)
    results["Baseline 0 (Hotspot Heuristic)"] = evaluate_model_performance(y_test, hotspot_scores, test_df)

    # 2. Spatial Proximity Heuristic
    spatial_model = SpatialProximityBaseline()
    spatial_scores = spatial_model.predict_proba(test_df)
    results["Baseline 1 (Spatial Proximity)"] = evaluate_model_performance(y_test, spatial_scores, test_df)

    # 3. Logistic Regression
    X_train_scaled = pipeline.transform(train_df, scale_numeric=True)
    X_test_scaled = pipeline.transform(test_df, scale_numeric=True)

    lr = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    lr_scores = lr.predict_proba(X_test_scaled)[:, 1]
    results["Baseline 2 (Logistic Regression)"] = evaluate_model_performance(y_test, lr_scores, test_df)

    # 4. Random Forest
    X_train = pipeline.transform(train_df, scale_numeric=False)
    X_test = pipeline.transform(test_df, scale_numeric=False)

    rf = RandomForestClassifier(n_estimators=100, max_depth=8, class_weight="balanced", random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_scores = rf.predict_proba(X_test)[:, 1]
    results["Baseline 3 (Random Forest)"] = evaluate_model_performance(y_test, rf_scores, test_df)

    return results

if __name__ == "__main__":
    from src.evaluation.metrics import format_metrics_table
    df = pd.read_parquet("data/synthetic/candidate_dataset.parquet")
    train_df = df[df["split"] == "train"]
    test_df = df[df["split"] == "test"]

    pipeline = FeaturePipeline.load()
    print("Evaluating Baseline Models on Out-Of-Time Test Set...")
    results = run_all_baselines(train_df, test_df, pipeline)
    print("\n" + format_metrics_table(results))
