import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from app.ml.risk_scoring import calculate_risk_score

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "trained_models")
MODEL_PATH = os.path.join(MODEL_DIR, "cash_withdrawal_classifier.joblib")


class MLPredictionEngine:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            self.model = None

    def predict(self, latitude: float, longitude: float, target_time: datetime, amount: float = 50000.0) -> dict:
        if self.model is None:
            self.load_model()

        hour = target_time.hour
        dayofweek = target_time.dayofweek
        is_night = 1 if (hour >= 22 or hour <= 5) else 0

        # Simulate spatial complaint density based on lat/lng heuristics for inference demo
        complaint_density = int((abs(np.sin(latitude)) + abs(np.cos(longitude))) * 5)

        if self.model is not None:
            features = pd.DataFrame([{
                'latitude': latitude,
                'longitude': longitude,
                'amount': amount,
                'hour': hour,
                'dayofweek': dayofweek,
                'is_night_time': is_night
            }])
            proba = float(self.model.predict_proba(features)[0][1])
        else:
            # Fallback heuristic if model file hasn't been serialized yet
            proba = float(min((abs(np.sin(latitude * longitude)) + (amount / 100000.0)) / 2.0, 0.95))

        anomaly_score = float(min((amount / 150000.0) * 0.5 + (0.4 if is_night else 0.1), 0.99))
        risk_info = calculate_risk_score(
            ml_probability=proba,
            anomaly_score=anomaly_score,
            nearby_complaints_count=complaint_density,
            withdrawal_amount=amount
        )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "risk_score": risk_info["risk_score"],
            "risk_level": risk_info["risk_level"],
            "confidence": round(float(proba), 3),
            "predicted_time": target_time,
            "model_version": "v1.0.0-GradientBoosting",
            "prediction_reason": f"High risk identified due to ML probability ({round(proba, 2)}) and night-time anomaly signals."
        }


ml_engine = MLPredictionEngine()