"""
src/explainability/explainer.py
TreeSHAP explainability engine for cybercrime cash-out prediction.
Provides:
1. Global feature importance (mean absolute SHAP)
2. Local candidate-level explanations (top positive & negative factor contributions)
3. Law-enforcement friendly factor descriptions adhering strictly to:
   "contributed to the model prediction" (no causal claims).
Supports v1.0.0 and v2.0.0 models.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import shap
from typing import List, Dict, Any, Optional

FACTOR_DESCRIPTIONS = {
    "dist_last_activity_to_candidate_km": "Close geographic proximity to last known fraudulent transaction",
    "dist_victim_to_candidate_km": "Proximity to victim's registered geographic location",
    "bank_match_flag": "Candidate ATM operator matches cashout mule bank network",
    "bank_monthly_cash_vol": "Bank network exhibits high cash disbursement volume in RBI statistics",
    "ncrb_state_cybercrime_rate": "High state-level cybercrime rate in official NCRB records",
    "ncrb_atm_fraud_cases": "State exhibits high ATM/card fraud incidents in NCRB context",
    "location_type": "Terminal type (CRM recycler machines allow larger cash withdrawals)",
    "mule_link_score": "Account network exhibits strong links to known mule account clusters",
    "mule_graph_degree": "High network connectivity in flagged mule account graph",
    "tx_count_last_1h": "Rapid transfer burst observed in the past hour",
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
    "amount_deviation_score": "Transaction amount unusually large for account profile",
    "atm_density_within_2km": "High local density of cash disbursement points",
    "time_since_complaint_min": "Critical early post-complaint time window",
    "time_since_last_txn_min": "Recent active transfer activity prior to prediction",
    "hour_of_day": "Withdrawal timing matches nocturnal/peak cyber-fraud hours",
    "day_of_week": "Timing aligns with weekend/holiday banking vulnerability",
    "is_weekend": "Weekend timing when branch intervention is delayed",
    "fraud_type": "Scam methodology profile",
    "last_channel": "Channel used for the latest fraudulent transfer",
    "population_group": "Locality classification (Metro/Urban hub preference)"
}

class SHAPExplainer:
    """Computes SHAP explanations for Tree models using TreeSHAP."""
    def __init__(
        self,
        model_path: Optional[str] = None,
        feature_schema_path: Optional[str] = None,
        version: str = "v2.0.0"
    ):
        self.version = version
        if model_path is None or not os.path.exists(model_path):
            candidate_model_paths = [
                f"models/{version}/model_{version}.joblib",
                f"artifacts/model/model_{version}.joblib",
                f"../artifacts/model/model_{version}.joblib",
                os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../models/{version}/model_{version}.joblib")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../artifacts/model/model_{version}.joblib"))
            ]
            for p in candidate_model_paths:
                if os.path.exists(p):
                    model_path = p
                    break

        if feature_schema_path is None or not os.path.exists(feature_schema_path):
            candidate_schema_paths = [
                f"models/{version}/feature_schema_{version}.json",
                f"artifacts/model/feature_schema_{version}.json",
                f"../artifacts/model/feature_schema_{version}.json",
                os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../models/{version}/feature_schema_{version}.json")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../artifacts/model/feature_schema_{version}.json"))
            ]
            for p in candidate_schema_paths:
                if os.path.exists(p):
                    feature_schema_path = p
                    break

        if model_path is None or not os.path.exists(model_path):
            # Fallback to v1
            model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../artifacts/model/model_v1.0.0.joblib"))
            feature_schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../artifacts/model/feature_schema_v1.0.0.json"))

        self.model = joblib.load(model_path)
        with open(feature_schema_path, "r") as f:
            schema = json.load(f)
        self.feature_names = schema["feature_names"]
        self.explainer = shap.TreeExplainer(self.model)

    def explain_candidates(
        self,
        X_matrix: np.ndarray,
        top_factors_count: int = 4
    ) -> List[List[Dict[str, Any]]]:
        """
        Computes local SHAP explanations for each row in X_matrix.
        Returns top contributing factors per candidate with directional contribution.
        """
        shap_values = self.explainer.shap_values(X_matrix)
        if isinstance(shap_values, list):
            sv = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        elif len(shap_values.shape) == 3:
            sv = shap_values[:, :, 1]
        else:
            sv = shap_values

        explanations = []
        for row_idx in range(len(X_matrix)):
            row_shap = sv[row_idx]
            top_indices = np.argsort(np.abs(row_shap))[::-1][:top_factors_count]

            factors = []
            for rank_idx, feat_idx in enumerate(top_indices):
                feat_name = self.feature_names[feat_idx]
                val = X_matrix[row_idx, feat_idx]
                val_shap = float(row_shap[feat_idx])
                direction = "increased risk" if val_shap > 0 else "decreased risk"
                readable_desc = FACTOR_DESCRIPTIONS.get(feat_name, feat_name.replace("_", " ").capitalize())

                factors.append({
                    "feature": feat_name,
                    "factor_name": feat_name,
                    "contribution": round(val_shap, 4),
                    "shap_value": round(val_shap, 4),
                    "impact": "INCREASES_RISK" if val_shap > 0 else "DECREASES_RISK",
                    "direction": "INCREASES_RISK" if val_shap > 0 else "DECREASES_RISK",
                    "contribution_direction": direction,
                    "description": readable_desc,
                    "impact_statement": f"{readable_desc} contributed to the model prediction ({direction})",
                    "feature_value": round(float(val), 2) if isinstance(val, (int, float, np.number)) else str(val),
                    "is_positive": val_shap > 0
                })
            explanations.append(factors)
        return explanations

    def compute_global_importance(self, X_sample: np.ndarray, output_path: str = None) -> List[Dict[str, Any]]:
        """Computes and saves global mean absolute SHAP feature importances."""
        shap_values = self.explainer.shap_values(X_sample)
        if isinstance(shap_values, list):
            sv = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        elif len(shap_values.shape) == 3:
            sv = shap_values[:, :, 1]
        else:
            sv = shap_values

        mean_abs_shap = np.mean(np.abs(sv), axis=0)
        sorted_indices = np.argsort(mean_abs_shap)[::-1]

        importance_list = []
        for idx in sorted_indices:
            feat_name = self.feature_names[idx]
            importance_list.append({
                "feature": feat_name,
                "importance": round(float(mean_abs_shap[idx]), 5),
                "description": FACTOR_DESCRIPTIONS.get(feat_name, feat_name)
            })

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(importance_list, f, indent=2)
            print(f"Global SHAP feature importance saved to {output_path}")

        return importance_list
