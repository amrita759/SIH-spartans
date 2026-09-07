"""
src/models/main_model.py
Main LightGBM Gradient Boosted Decision Tree Model for cybercrime cash-out prediction.
Trained with early stopping on validation split. Evaluated on out-of-time test set.
Exports versioned model artifacts and metadata.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import json
import joblib
import datetime
import numpy as np
import pandas as pd
import lightgbm as lgb
from typing import Dict, Any, Optional, Tuple

from src.features.feature_pipeline import FeaturePipeline
from src.evaluation.metrics import evaluate_model_performance, format_metrics_table

class MainModelTrainer:
    """Trains, evaluates, and packages the main LightGBM model."""
    def __init__(
        self,
        version: str = "v1.0.0",
        artifact_dir: Optional[str] = None,
        pipeline: Optional[FeaturePipeline] = None
    ):
        self.version = version
        self.artifact_dir = artifact_dir
        if pipeline is not None:
            self.pipeline = pipeline
        else:
            self.pipeline = FeaturePipeline.load(artifact_dir=artifact_dir, version=version)
        self.model = None

    def train(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        params: Dict[str, Any] = None
    ) -> lgb.LGBMClassifier:
        """Fits LightGBM with early stopping on validation set."""
        X_train = self.pipeline.transform(train_df, scale_numeric=False)
        y_train = train_df["target"].values

        X_val = self.pipeline.transform(val_df, scale_numeric=False)
        y_val = val_df["target"].values

        default_params = {
            "objective": "binary",
            "metric": "average_precision",
            "boosting_type": "gbdt",
            "n_estimators": 350,
            "learning_rate": 0.04,
            "num_leaves": 31,
            "max_depth": 6,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "scale_pos_weight": 15.0,
            "random_state": 42,
            "verbose": -1
        }
        if params:
            default_params.update(params)

        print("Fitting LightGBM model with parameters:", default_params)
        self.model = lgb.LGBMClassifier(**default_params)
        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(stopping_rounds=30, verbose=False)]
        )
        return self.model

    def evaluate(self, test_df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluates model performance on out-of-time test dataset."""
        if self.model is None:
            raise ValueError("Model is not trained yet.")

        X_test = self.pipeline.transform(test_df, scale_numeric=False)
        y_test = test_df["target"].values

        scores = self.model.predict_proba(X_test)[:, 1]
        metrics = evaluate_model_performance(y_test, scores, test_df)
        return metrics, scores

    def save(
        self,
        metrics: Dict[str, Any],
        artifact_dir: str = "artifacts",
        data_stats: Dict[str, Any] = None
    ):
        """Saves model artifact, metadata, and evaluation metrics."""
        model_dir = os.path.join(artifact_dir, "model")
        metadata_dir = os.path.join(artifact_dir, "metadata")
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(metadata_dir, exist_ok=True)

        model_path = os.path.join(model_dir, f"model_{self.version}.joblib")
        joblib.dump(self.model, model_path)
        print(f"Saved model artifact to {model_path}")

        # Model metadata
        metadata = {
            "model_name": "LightGBM_Cashout_Predictor",
            "model_version": self.version,
            "created_at": datetime.datetime.now().isoformat(),
            "target": "target (cashout at candidate location during T -> T+6h)",
            "prediction_horizon_hours": 6,
            "features": self.pipeline.get_feature_names(),
            "total_features": len(self.pipeline.get_feature_names()),
            "best_iteration": int(getattr(self.model, "best_iteration_", 0)),
            "data_summary": data_stats or {}
        }
        with open(os.path.join(metadata_dir, "model_metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        with open(os.path.join(metadata_dir, "metrics.json"), "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"Saved metadata and metrics to {metadata_dir}")

if __name__ == "__main__":
    df = pd.read_parquet("data/synthetic/candidate_dataset.parquet")
    train_df = df[df["split"] == "train"]
    val_df = df[df["split"] == "val"]
    test_df = df[df["split"] == "test"]

    trainer = MainModelTrainer(version="v1.0.0")
    trainer.train(train_df, val_df)
    test_metrics, test_scores = trainer.evaluate(test_df)
    
    data_stats = {
        "train_cases": int(train_df["case_id"].nunique()),
        "val_cases": int(val_df["case_id"].nunique()),
        "test_cases": int(test_df["case_id"].nunique()),
        "train_rows": len(train_df),
        "test_rows": len(test_df)
    }
    trainer.save(test_metrics, data_stats=data_stats)

    print("\n--- LightGBM Main Model Out-Of-Time Test Results ---")
    results = {"Main Model (LightGBM)": test_metrics}
    print(format_metrics_table(results))
