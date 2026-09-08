"""
tests/test_model.py
Verifies model loading and scoring.
"""

import pytest
import joblib
import numpy as np
import pandas as pd
from src.features.feature_pipeline import FeaturePipeline

def test_model_loading_and_inference():
    df = pd.read_parquet("data/synthetic/candidate_dataset.parquet").head(10)

    # 1. Verify v1.0.0 (25 features)
    pipeline_v1 = FeaturePipeline.load(version="v1.0.0")
    model_v1 = joblib.load("artifacts/model/model_v1.0.0.joblib")
    X1 = pipeline_v1.transform(df)
    assert X1.shape[1] == 25
    scores1 = model_v1.predict_proba(X1)[:, 1]
    assert len(scores1) == 10
    assert (scores1 >= 0.0).all() and (scores1 <= 1.0).all()

    # 2. Verify v2.0.0 (30 features with Bank & Crime Context)
    pipeline_v2 = FeaturePipeline.load(version="v2.0.0")
    model_v2 = joblib.load("artifacts/model/model_v2.0.0.joblib")
    X2 = pipeline_v2.transform(df)
    assert X2.shape[1] == 30
    scores2 = model_v2.predict_proba(X2)[:, 1]
    assert len(scores2) == 10
    assert (scores2 >= 0.0).all() and (scores2 <= 1.0).all()
