"""
src/explainability/explainer.py
TreeSHAP explainability engine for cybercrime cash-out prediction.
Provides:
1. Global feature importance (mean absolute SHAP)
2. Local candidate-level explanations (top positive & negative factor contributions)
3. Law-enforcement friendly factor descriptions
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import json
import joblib
import numpy as np
import pandas as pd
import shap
from typing import List, Dict, Any

FACTOR_DESCRIPTIONS = {
    "dist_last_activity_to_candidate_km": "Close geographic proximity to last known fraudulent transaction",
    "dist_victim_to_candidate_km": "Proximity to victim's registered geographic location",
    "mule_link_score": "Account strongly linked to known mule account syndicates",
    "mule_graph_degree": "High network connectivity in flagged account graph",
    "tx_count_last_1h": "Rapid transfer burst observed in the last hour",
    "tx_count_last_6h": "Elevated transaction frequency across the past 6 hours",
    "tx_amount_last_1h": "High monetary outflow during the past hour",
    "tx_amount_last_6h": "Cumulative transferred amount in past 6 hours",
    "fraud_amount": "Magnitude of reported cybercrime complaint amount",
    "cumulative_known_transfer_amount": "High cumulative transferred funds into mule layer",
    "transfer_count": "Multiple layering hops tracked before cash-out attempt",
    "amount_velocity_ratio": "High proportion of stolen funds transferred in last hour",
    "hist_atm_fraud_count_90d": "Historical repeat cash-out incidents recorded at this ATM",
    "hist_atm_hour_affinity": "Matching historical cash-out time-of-day pattern",
    "burstiness_score": "Abnormal velocity spike relative to recent baseline",
    "amount_deviation_score": "Transaction amount unusually large for account history",
    "atm_density_within_2km": "High local density of cash disbursement points",
    "time_since_complaint_min": "Critical post-complaint time window",
    "time_since_last_txn_min": "Recent active transfer activity",
    "hour_of_day": "Withdrawal timing matches nocturnal/peak cyber-fraud hours",
    "day_of_week": "Timing aligns with weekend/holiday banking vulnerability",
    "is_weekend": "Weekend timing when branch intervention is delayed",
    "fraud_type": "Scam methodology profile",
    "last_channel": "Channel used for the latest fraudulent transfer",
    "population_group": "Locality type (Metro/Urban hub preference)"
}

class SHAPExplainer:
    """Computes SHAP explanations for Tree models."""
    def __init__(
        self,
        model_path: str = "artifacts/model/model_v1.0.0.joblib",
        feature_schema_path: str = "artifacts/model/feature_schema_v1.0.0.json"
    ):
        self.model = joblib.load(model_path)
        with open(feature_schema_path, "r") as f:
            schema = json.load(f)
        self.feature_names = schema["feature_names"]
        self.explainer = shap.TreeExplainer(self.model)

    def explain_candidates(
        self,
        X_matrix: np.ndarray,
        top_factors_count: int = 3
    ) -> List[List[Dict[str, Any]]]:
        """
        Computes local SHAP explanations for each row in X_matrix.
        Returns top contributing factors per candidate.
        """
        shap_values = self.explainer.shap_values(X_matrix)
        # For binary classification, shap_values may be list [class0, class1] or array of class1
        if isinstance(shap_values, list):
            sv = shap_values[1]
        elif len(shap_values.shape) == 3:
            sv = shap_values[:, :, 1]
        else:
            sv = shap_values

        explanations = []
        for i in range(len(X_matrix)):
            row_sv = sv[i]
            # Sort factors by absolute contribution magnitude
            top_indices = np.argsort(np.abs(row_sv))[::-1][:top_factors_count]
            factors = []
            for idx in top_indices:
                feat = self.feature_names[idx]
                contrib = round(float(row_sv[idx]), 3)
                desc = FACTOR_DESCRIPTIONS.get(feat, f"Contribution of {feat}")
                factors.append({
                    "feature": feat,
                    "contribution": contrib,
                    "impact": "INCREASES_RISK" if contrib > 0 else "DECREASES_RISK",
                    "description": desc
                })
            explanations.append(factors)

        return explanations

    def compute_global_importance(
        self,
        X_sample: np.ndarray,
        save_path: str = "artifacts/explainability/global_importance.json"
    ) -> Dict[str, float]:
        """Computes and saves mean absolute SHAP values."""
        shap_values = self.explainer.shap_values(X_sample)
        if isinstance(shap_values, list):
            sv = shap_values[1]
        elif len(shap_values.shape) == 3:
            sv = shap_values[:, :, 1]
        else:
            sv = shap_values

        mean_abs_shap = np.mean(np.abs(sv), axis=0)
        importance_dict = {
            self.feature_names[i]: round(float(mean_abs_shap[i]), 4)
            for i in np.argsort(mean_abs_shap)[::-1]
        }

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(importance_dict, f, indent=2)
        print(f"Global feature importance saved to {save_path}")
        return importance_dict

if __name__ == "__main__":
    from src.features.feature_pipeline import FeaturePipeline
    pipeline = FeaturePipeline.load()
    df = pd.read_parquet("data/synthetic/candidate_dataset.parquet")
    sample_df = df[df["split"] == "test"].head(100)
    X_sample = pipeline.transform(sample_df)

    explainer = SHAPExplainer()
    print("Computing global feature importance...")
    importance = explainer.compute_global_importance(X_sample)
    print("\nTop 5 Global Features by Mean |SHAP|:")
    for k, v in list(importance.items())[:5]:
        print(f"  {k}: {v}")

    print("\nLocal explanation sample for candidate 0:")
    sample_factors = explainer.explain_candidates(X_sample[:1])
    print(json.dumps(sample_factors[0], indent=2))
