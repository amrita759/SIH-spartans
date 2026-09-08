"""
tests/test_features.py
Verifies feature pipeline integrity and leakage-free guarantees.
"""

import pytest
import numpy as np
import pandas as pd
from src.features.feature_pipeline import FeaturePipeline, NUMERICAL_FEATURES, CATEGORICAL_FEATURES

def test_feature_pipeline_fit_transform():
    df = pd.read_parquet("data/synthetic/candidate_dataset.parquet")
    train_df = df[df["split"] == "train"].head(100)
    test_df = df[df["split"] == "test"].head(20)

    pipeline = FeaturePipeline(version="v2.0.0_test")
    pipeline.fit(train_df)

    X_train = pipeline.transform(train_df)
    X_test = pipeline.transform(test_df)

    assert X_train.shape[1] == len(pipeline.numerical_features) + len(pipeline.categorical_features)
    assert X_test.shape[1] == len(pipeline.numerical_features) + len(pipeline.categorical_features)
    assert not np.isnan(X_train).any()
    assert not np.isnan(X_test).any()

def test_no_forbidden_leakage_columns_in_pipeline():
    pipeline = FeaturePipeline()
    feature_names = set(pipeline.get_feature_names())
    banned_keywords = ["actual", "target", "withdrawal_time", "withdrawal_amount", "cashout_atm"]
    for feat in feature_names:
        for banned in banned_keywords:
            assert banned not in feat.lower(), f"Feature {feat} contains banned leakage keyword {banned}"
