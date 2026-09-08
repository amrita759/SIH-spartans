"""
src/features/feature_pipeline.py
Reusable, leakage-free feature processing pipeline.
Preprocessors are fitted strictly on the chronological training split.
Saves versioned feature schemas and transformers to artifacts/model/ and models/.
Supports v1.0.0 and v2.0.0 with backward compatibility.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from sklearn.preprocessing import StandardScaler, OrdinalEncoder

# Version 1.0.0 Feature Schema (25 features)
V1_NUMERICAL_FEATURES = [
    "hour_of_day", "day_of_week", "is_weekend",
    "time_since_complaint_min", "time_since_last_txn_min",
    "tx_count_last_1h", "tx_count_last_6h",
    "tx_amount_last_1h", "tx_amount_last_6h",
    "transfer_count", "amount_velocity_ratio",
    "fraud_amount", "cumulative_known_transfer_amount",
    "dist_victim_to_candidate_km", "dist_last_activity_to_candidate_km",
    "atm_density_within_2km",
    "hist_atm_fraud_count_90d", "hist_atm_hour_affinity",
    "burstiness_score", "amount_deviation_score",
    "mule_link_score", "mule_graph_degree"
]
V1_CATEGORICAL_FEATURES = [
    "fraud_type", "last_channel", "population_group"
]

# Version 2.0.0 Feature Schema (30 features: adds real Bank & Crime Context, location_type)
V2_NUMERICAL_FEATURES = [
    # Temporal
    "hour_of_day", "day_of_week", "is_weekend",
    "time_since_complaint_min", "time_since_last_txn_min",
    # Velocity
    "tx_count_last_1h", "tx_count_last_6h",
    "tx_amount_last_1h", "tx_amount_last_6h",
    "transfer_count", "amount_velocity_ratio", "burstiness_score",
    # Financial
    "fraud_amount", "cumulative_known_transfer_amount", "amount_deviation_score",
    # Spatial
    "dist_victim_to_candidate_km", "dist_last_activity_to_candidate_km", "atm_density_within_2km",
    # Bank Context (from RBI monthly statistics & accounts)
    "bank_match_flag", "bank_monthly_cash_vol",
    # Crime Context (from NCRB tables)
    "ncrb_state_cybercrime_rate", "ncrb_atm_fraud_cases",
    # Historical
    "hist_atm_fraud_count_90d", "hist_atm_hour_affinity",
    # Network
    "mule_graph_degree", "mule_link_score"
]
V2_CATEGORICAL_FEATURES = [
    "fraud_type", "last_channel", "location_type", "population_group"
]

NUMERICAL_FEATURES = V2_NUMERICAL_FEATURES
CATEGORICAL_FEATURES = V2_CATEGORICAL_FEATURES

class FeaturePipeline:
    """
    Leakage-free feature transformer. Fits only on training data.
    Ensures exact feature ordering for train, validation, test, and FastAPI inference.
    """
    def __init__(self, version: str = "v2.0.0"):
        self.version = version
        if "v1" in version:
            self.numerical_features = list(V1_NUMERICAL_FEATURES)
            self.categorical_features = list(V1_CATEGORICAL_FEATURES)
        else:
            self.numerical_features = list(V2_NUMERICAL_FEATURES)
            self.categorical_features = list(V2_CATEGORICAL_FEATURES)

        self.all_feature_names = self.numerical_features + self.categorical_features
        self.scaler = StandardScaler()
        self.encoder = OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1
        )
        self.is_fitted = False

    def fit(self, df_train: pd.DataFrame):
        """Fit preprocessors strictly on training split."""
        X_num = df_train[self.numerical_features].fillna(0.0).values
        self.scaler.fit(X_num)

        X_cat = df_train[self.categorical_features].fillna("UNKNOWN").astype(str).values
        self.encoder.fit(X_cat)

        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame, scale_numeric: bool = False) -> np.ndarray:
        """
        Transforms input dataframe into feature array.
        For tree models (LightGBM/RF), scale_numeric is usually False to preserve interpretability.
        For Logistic Regression, scale_numeric is True.
        """
        if not self.is_fitted:
            raise ValueError("FeaturePipeline is not fitted yet. Call fit() first.")

        df_copy = df.copy()
        for col in self.numerical_features:
            if col not in df_copy.columns:
                df_copy[col] = 0.0
        for col in self.categorical_features:
            if col not in df_copy.columns:
                df_copy[col] = "UNKNOWN"

        X_num = df_copy[self.numerical_features].fillna(0.0).values
        if scale_numeric:
            X_num = self.scaler.transform(X_num)

        X_cat = df_copy[self.categorical_features].fillna("UNKNOWN").astype(str).values
        X_cat_encoded = self.encoder.transform(X_cat)

        return np.hstack([X_num, X_cat_encoded])

    def get_feature_names(self) -> List[str]:
        return self.all_feature_names

    def save(self, artifact_dir: str = "artifacts/model"):
        """Saves pipeline artifacts and schema JSON to both artifact_dir and models/ directory."""
        os.makedirs(artifact_dir, exist_ok=True)
        joblib.dump(self.scaler, os.path.join(artifact_dir, f"scaler_{self.version}.joblib"))
        joblib.dump(self.encoder, os.path.join(artifact_dir, f"encoder_{self.version}.joblib"))

        schema = {
            "version": self.version,
            "feature_names": self.all_feature_names,
            "numerical_features": self.numerical_features,
            "categorical_features": self.categorical_features,
            "total_features": len(self.all_feature_names)
        }
        with open(os.path.join(artifact_dir, f"feature_schema_{self.version}.json"), "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Feature pipeline and schema ({self.version}) saved to {artifact_dir}")

    @classmethod
    def load(cls, artifact_dir: Optional[str] = None, version: str = "v2.0.0"):
        """Loads fitted transformers and restores pipeline with path auto-resolution."""
        candidate_dirs = []
        if artifact_dir:
            candidate_dirs.append(artifact_dir)
            candidate_dirs.append(os.path.join("..", artifact_dir))

        candidate_dirs.extend([
            f"models/{version}",
            f"models/current",
            "artifacts/model",
            "../artifacts/model",
            os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../models/{version}")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../artifacts/model"))
        ])

        resolved_dir = None
        for cdir in candidate_dirs:
            scaler_path = os.path.join(cdir, f"scaler_{version}.joblib")
            encoder_path = os.path.join(cdir, f"encoder_{version}.joblib")
            if os.path.exists(scaler_path) and os.path.exists(encoder_path):
                resolved_dir = cdir
                break

        if resolved_dir is None:
            # Fallback to v1 if v2 not yet built
            if version != "v1.0.0":
                try:
                    return cls.load(artifact_dir=artifact_dir, version="v1.0.0")
                except Exception:
                    pass
            raise FileNotFoundError(
                f"Fitted transformers for version {version} not found in: {candidate_dirs}"
            )

        pipeline = cls(version=version)
        schema_path = os.path.join(resolved_dir, f"feature_schema_{version}.json")
        if os.path.exists(schema_path):
            with open(schema_path) as f:
                schema = json.load(f)
                pipeline.numerical_features = schema.get("numerical_features", pipeline.numerical_features)
                pipeline.categorical_features = schema.get("categorical_features", pipeline.categorical_features)
                pipeline.all_feature_names = schema.get("feature_names", pipeline.all_feature_names)

        pipeline.scaler = joblib.load(os.path.join(resolved_dir, f"scaler_{version}.joblib"))
        pipeline.encoder = joblib.load(os.path.join(resolved_dir, f"encoder_{version}.joblib"))
        pipeline.is_fitted = True
        return pipeline

if __name__ == "__main__":
    dataset_path = "data/synthetic/candidate_dataset.parquet"
    df = pd.read_parquet(dataset_path)
    train_df = df[df["split"] == "train"]
    print(f"Fitting FeaturePipeline v2.0.0 on {len(train_df)} training rows...")
    pipeline = FeaturePipeline(version="v2.0.0")
    pipeline.fit(train_df)
    pipeline.save(artifact_dir="artifacts/model")
    pipeline.save(artifact_dir="models/v2")
    pipeline.save(artifact_dir="models/current")
    print("Features (30 total):", pipeline.get_feature_names())
