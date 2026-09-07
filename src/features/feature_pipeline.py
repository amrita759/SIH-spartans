"""
src/features/feature_pipeline.py
Reusable, leakage-free feature processing pipeline.
Preprocessors are fitted strictly on the chronological training split.
Saves versioned feature schemas and transformers to artifacts/model/.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import json
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from sklearn.preprocessing import StandardScaler, OrdinalEncoder

NUMERICAL_FEATURES = [
    # Temporal
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "time_since_complaint_min",
    "time_since_last_txn_min",
    # Velocity
    "tx_count_last_1h",
    "tx_count_last_6h",
    "tx_amount_last_1h",
    "tx_amount_last_6h",
    "transfer_count",
    "amount_velocity_ratio",
    # Financial
    "fraud_amount",
    "cumulative_known_transfer_amount",
    # Spatial
    "dist_victim_to_candidate_km",
    "dist_last_activity_to_candidate_km",
    "atm_density_within_2km",
    # Historical
    "hist_atm_fraud_count_90d",
    "hist_atm_hour_affinity",
    # Behavioural
    "burstiness_score",
    "amount_deviation_score",
    # Network
    "mule_link_score",
    "mule_graph_degree"
]

CATEGORICAL_FEATURES = [
    "fraud_type",
    "last_channel",
    "population_group"
]

METADATA_COLS = [
    "case_id", "split", "prediction_time", "location_id",
    "location_name", "candidate_lat", "candidate_lon", "target"
]

class FeaturePipeline:
    """
    Leakage-free feature transformer. Fits only on training data.
    Ensures exact feature ordering for train, validation, test, and FastAPI inference.
    """
    def __init__(self, version: str = "v1.0.0"):
        self.version = version
        self.numerical_features = NUMERICAL_FEATURES
        self.categorical_features = CATEGORICAL_FEATURES
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
        For tree models (LightGBM/XGBoost/RF), scale_numeric is usually False to preserve interpretability.
        For Logistic Regression, scale_numeric is True.
        """
        if not self.is_fitted:
            raise ValueError("FeaturePipeline is not fitted yet. Call fit() first.")

        # Ensure all columns exist
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
        """Saves pipeline artifacts and schema JSON."""
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
        print(f"Feature pipeline and schema saved to {artifact_dir}")

    @classmethod
    def load(cls, artifact_dir: Optional[str] = None, version: str = "v1.0.0"):
        """Loads fitted transformers and restores pipeline with path auto-resolution."""
        candidate_dirs = []
        if artifact_dir:
            candidate_dirs.append(artifact_dir)
            candidate_dirs.append(os.path.join("..", artifact_dir))
        
        # Default fallback locations
        candidate_dirs.extend([
            "artifacts/model",
            "../artifacts/model",
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
            raise FileNotFoundError(
                f"Fitted transformers not found in any searched locations: {candidate_dirs}"
            )

        pipeline = cls(version=version)
        pipeline.scaler = joblib.load(os.path.join(resolved_dir, f"scaler_{version}.joblib"))
        pipeline.encoder = joblib.load(os.path.join(resolved_dir, f"encoder_{version}.joblib"))
        pipeline.is_fitted = True
        return pipeline

if __name__ == "__main__":
    dataset_path = "data/synthetic/candidate_dataset.parquet"
    df = pd.read_parquet(dataset_path)
    train_df = df[df["split"] == "train"]
    val_df = df[df["split"] == "val"]
    test_df = df[df["split"] == "test"]

    print(f"Fitting FeaturePipeline on {len(train_df)} training rows...")
    pipeline = FeaturePipeline(version="v1.0.0")
    pipeline.fit(train_df)
    pipeline.save()

    X_test = pipeline.transform(test_df)
    print("X_test transformed shape:", X_test.shape)
    print("Features:", pipeline.get_feature_names())
