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
    pipeline = FeaturePipeline.load()
    model = joblib.load("artifacts/model/model_v1.0.0.joblib")
    
    df = pd.read_parquet("data/synthetic/candidate_dataset.parquet").head(10)
    X = pipeline.transform(df)
    scores = model.predict_proba(X)[:, 1]

    assert len(scores) == 10
    assert (scores >= 0.0).all() and (scores <= 1.0).all()
