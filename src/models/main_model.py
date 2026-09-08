"""
src/models/main_model.py
Main LightGBM Gradient Boosted Decision Tree Model for cybercrime cash-out prediction.
Trained with early stopping on validation split. Evaluated on out-of-time test set.
Benchmarks against all progressive baselines (Spatial Proximity, Historical Hotspot,
Logistic Regression, Random Forest, Raw LightGBM, and Composite LightGBM + Spatial).
Exports versioned model artifacts and metadata for v2.0.0.
"""

import os
import sys
import json
import joblib
import datetime
import numpy as np
import pandas as pd
import lightgbm as lgb
from typing import Dict, Any, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.features.feature_pipeline import FeaturePipeline
from src.evaluation.metrics import evaluate_model_performance, format_metrics_table, compute_lead_time_metrics
from src.models.baselines import HotspotBaseline, SpatialProximityBaseline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from src.explainability.explainer import SHAPExplainer

class MainModelTrainer:
    """Trains, evaluates, and packages the main LightGBM model and baseline benchmarks."""
    def __init__(
        self,
        version: str = "v2.0.0",
        artifact_dir: Optional[str] = None,
        pipeline: Optional[FeaturePipeline] = None
    ):
        self.version = version
        self.artifact_dir = artifact_dir or "artifacts"
        if pipeline is not None:
            self.pipeline = pipeline
        else:
            self.pipeline = FeaturePipeline(version=version)
        self.model = None

    def train(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        params: Dict[str, Any] = None
    ) -> lgb.LGBMClassifier:
        """Fits LightGBM with early stopping on validation set."""
        print(f"Fitting FeaturePipeline ({self.version}) on training data...")
        self.pipeline.fit(train_df)

        X_train = self.pipeline.transform(train_df, scale_numeric=False)
        y_train = train_df["target"].values

        X_val = self.pipeline.transform(val_df, scale_numeric=False)
        y_val = val_df["target"].values

        default_params = {
            "objective": "binary",
            "metric": "average_precision",
            "boosting_type": "gbdt",
            "n_estimators": 400,
            "learning_rate": 0.035,
            "num_leaves": 31,
            "max_depth": 6,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "scale_pos_weight": 12.0,
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
            callbacks=[lgb.early_stopping(stopping_rounds=35, verbose=False)]
        )
        return self.model

    def evaluate(self, test_df: pd.DataFrame) -> Tuple[Dict[str, Any], np.ndarray]:
        """Evaluates trained model on a single test DataFrame."""
        X_test = self.pipeline.transform(test_df)
        df_named = pd.DataFrame(X_test, columns=self.pipeline.get_feature_names())
        scores = self.model.predict_proba(df_named)[:, 1]
        metrics = evaluate_model_performance(test_df["target"].values, scores, test_df)
        return metrics, scores

    def evaluate_all(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame
    ) -> Tuple[Dict[str, Dict[str, Any]], np.ndarray]:
        """
        Runs comprehensive comparative benchmark on held-out test split across:
        1. Spatial Proximity Baseline
        2. Historical Hotspot Baseline
        3. Regularized Logistic Regression
        4. Random Forest
        5. LightGBM (Raw ML)
        6. LightGBM + Spatial (Composite Ranking)
        """
        y_train = train_df["target"].values
        y_test = test_df["target"].values
        results = {}

        print("\n--- Evaluating Baseline Models on Out-Of-Time Test Split ---")
        # 1. Hotspot Heuristic
        hotspot = HotspotBaseline()
        hotspot_scores = hotspot.predict_proba(test_df)
        results["Baseline 0 (Hotspot Heuristic)"] = evaluate_model_performance(y_test, hotspot_scores, test_df)

        # 2. Spatial Proximity
        spatial = SpatialProximityBaseline()
        spatial_scores = spatial.predict_proba(test_df)
        results["Baseline 1 (Spatial Proximity)"] = evaluate_model_performance(y_test, spatial_scores, test_df)

        # 3. Logistic Regression
        X_train_scaled = self.pipeline.transform(train_df, scale_numeric=True)
        X_test_scaled = self.pipeline.transform(test_df, scale_numeric=True)
        lr = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
        lr.fit(X_train_scaled, y_train)
        lr_scores = lr.predict_proba(X_test_scaled)[:, 1]
        results["Baseline 2 (Logistic Regression)"] = evaluate_model_performance(y_test, lr_scores, test_df)

        # 4. Random Forest
        X_train = self.pipeline.transform(train_df, scale_numeric=False)
        X_test = self.pipeline.transform(test_df, scale_numeric=False)
        rf = RandomForestClassifier(n_estimators=100, max_depth=8, class_weight="balanced", random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        rf_scores = rf.predict_proba(X_test)[:, 1]
        results["Baseline 3 (Random Forest)"] = evaluate_model_performance(y_test, rf_scores, test_df)

        # 5. Raw LightGBM
        raw_lgbm_scores = self.model.predict_proba(X_test)[:, 1]
        results["Main Model (Raw LightGBM)"] = evaluate_model_performance(y_test, raw_lgbm_scores, test_df)

        # 6. Composite LightGBM + Spatial Ranking
        # Combines raw ML prediction with spatial proximity prior
        composite_scores = 0.60 * raw_lgbm_scores + 0.40 * spatial_scores
        results["Main Model (LightGBM + Spatial Composite)"] = evaluate_model_performance(y_test, composite_scores, test_df)

        return results, raw_lgbm_scores

    def save(
        self,
        all_results: Dict[str, Dict[str, Any]],
        data_stats: Dict[str, Any] = None,
        lead_time_stats: Dict[str, Any] = None
    ):
        """Saves model artifacts, transformers, metadata, and benchmarks across versioned directories."""
        save_dirs = [
            f"models/{self.version}",
            "models/current",
            "artifacts/model"
        ]

        for d in save_dirs:
            os.makedirs(d, exist_ok=True)
            model_file = os.path.join(d, f"model_{self.version}.joblib")
            joblib.dump(self.model, model_file)
            self.pipeline.save(artifact_dir=d)
            print(f"  Exported model and preprocessors to {d}")

        # Metadata
        main_metrics = all_results.get("Main Model (LightGBM + Spatial Composite)") or all_results.get("Main Model (Raw LightGBM)")
        metadata = {
            "model_name": "LightGBM_Cashout_Predictor",
            "model_version": self.version,
            "created_at": datetime.datetime.now().isoformat(),
            "target": "target (cashout at candidate location during T -> T+6h)",
            "prediction_horizon_hours": 6,
            "features": self.pipeline.get_feature_names(),
            "total_features": len(self.pipeline.get_feature_names()),
            "best_iteration": int(getattr(self.model, "best_iteration_", 0)),
            "data_summary": data_stats or {},
            "lead_time_summary": lead_time_stats or {},
            "benchmarks": all_results
        }

        meta_dirs = ["artifacts/metadata", f"models/{self.version}", "models/current"]
        for md in meta_dirs:
            os.makedirs(md, exist_ok=True)
            with open(os.path.join(md, "model_metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)
            with open(os.path.join(md, "metrics.json"), "w") as f:
                json.dump(main_metrics, f, indent=2)
            with open(os.path.join(md, "baseline_comparison.json"), "w") as f:
                json.dump(all_results, f, indent=2)
        print("Saved metadata and baseline comparisons.")

if __name__ == "__main__":
    df = pd.read_parquet("data/synthetic/candidate_dataset.parquet")
    withdrawals_df = pd.read_csv("data/synthetic/withdrawals.csv")
    lead_stats = compute_lead_time_metrics(withdrawals_df)

    train_df = df[df["split"] == "train"]
    val_df = df[df["split"] == "val"]
    test_df = df[df["split"] == "test"]

    trainer = MainModelTrainer(version="v2.0.0")
    trainer.train(train_df, val_df)
    results, test_scores = trainer.evaluate_all(train_df, test_df)

    data_stats = {
        "train_cases": int(train_df["case_id"].nunique()),
        "val_cases": int(val_df["case_id"].nunique()),
        "test_cases": int(test_df["case_id"].nunique()),
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df)
    }

    trainer.save(results, data_stats=data_stats, lead_time_stats=lead_stats)

    print("\n=================== PROGRESSIVE MODEL BENCHMARKS ===================")
    print(format_metrics_table(results))
    print("\nLead Time Summary (Prototype):", lead_stats)

    # Compute Global SHAP Feature Importance
    print("\nComputing global TreeSHAP feature importance...")
    explainer = SHAPExplainer(
        model_path="models/v2.0.0/model_v2.0.0.joblib",
        feature_schema_path="models/v2.0.0/feature_schema_v2.0.0.json",
        version="v2.0.0"
    )
    X_test_sample = trainer.pipeline.transform(test_df.head(500), scale_numeric=False)
    explainer.compute_global_importance(X_test_sample, output_path="artifacts/explainability/global_importance.json")
    explainer.compute_global_importance(X_test_sample, output_path="models/v2.0.0/global_importance.json")
    print("[DONE] Main model training, benchmarking, and SHAP computation complete.")
