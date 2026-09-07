"""
api/routes/model_info.py
Model metadata and feature contract inspection endpoints.
"""

import os
import json
from fastapi import APIRouter, Depends
from api.schemas import ModelInfoResponse
from api.services.prediction_service import get_prediction_service, PredictionService

router = APIRouter(tags=["Model Info"])

@router.get("/model/info", response_model=ModelInfoResponse)
def get_model_info(service: PredictionService = Depends(get_prediction_service)):
    """
    Returns active model version, prediction window, feature list, and evaluation metrics.
    """
    metrics_path = os.path.join(service.artifact_dir, "metadata", "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
    else:
        metrics = {}

    return ModelInfoResponse(
        model_name=service.metadata.get("model_name", "LightGBM_Cashout_Predictor"),
        model_version=service.version,
        prediction_horizon_hours=service.metadata.get("prediction_horizon_hours", 6),
        supported_windows=[6, 12, 24],
        total_features=service.metadata.get("total_features", len(service.pipeline.get_feature_names())),
        feature_names=service.pipeline.get_feature_names(),
        created_at=service.metadata.get("created_at", ""),
        metrics_summary=metrics
    )
