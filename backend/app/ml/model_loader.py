"""
backend/app/ml/model_loader.py
Safe loader for trained LightGBM model, feature pipelines, metadata, and SHAP trees.
Auto-detects and prioritizes v2.0.0, with clean fallback to v1.0.0.
"""

import os
import json
import joblib
from typing import Dict, Any, Tuple
from src.features.feature_pipeline import FeaturePipeline

def resolve_artifact_path(relative_path: str) -> str:
    """Searches common relative locations to resolve artifact path."""
    candidates = [
        relative_path,
        os.path.join("..", relative_path),
        os.path.join("../..", relative_path),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../", relative_path))
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    raise FileNotFoundError(f"Artifact not found in candidate paths: {candidates}")

def load_ml_artifacts(version: str = "v2.0.0") -> Dict[str, Any]:
    """
    Loads all trained model weights, feature transformers, schema, and evaluation metrics once.
    """
    # Check if v2.0.0 exists; if not, fallback to v1.0.0
    try:
        model_path = resolve_artifact_path(f"artifacts/model/model_{version}.joblib")
        schema_path = resolve_artifact_path(f"artifacts/model/feature_schema_{version}.json")
    except FileNotFoundError:
        if version != "v1.0.0":
            version = "v1.0.0"
            model_path = resolve_artifact_path(f"artifacts/model/model_{version}.joblib")
            schema_path = resolve_artifact_path(f"artifacts/model/feature_schema_{version}.json")
        else:
            raise

    metadata_path = resolve_artifact_path("artifacts/metadata/model_metadata.json")
    metrics_path = resolve_artifact_path("artifacts/metadata/metrics.json")

    # Load model
    model = joblib.load(model_path)

    # Load Feature Pipeline
    pipeline = FeaturePipeline.load(
        artifact_dir=os.path.dirname(model_path),
        version=version
    )

    # Load Schema
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # Load Model Metadata
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Load Out-of-time Metrics
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    # Optional benchmarks
    benchmarks_path = resolve_artifact_path("artifacts/metadata/baseline_comparison.json")
    benchmarks = None
    if os.path.exists(benchmarks_path):
        with open(benchmarks_path, "r", encoding="utf-8") as f:
            benchmarks = json.load(f)

    return {
        "model": model,
        "pipeline": pipeline,
        "schema": schema,
        "metadata": metadata,
        "metrics": metrics,
        "benchmarks": benchmarks,
        "model_path": model_path,
        "schema_path": schema_path,
        "version": version
    }
