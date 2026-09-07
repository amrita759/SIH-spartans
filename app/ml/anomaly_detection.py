import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(contamination=contamination, random_state=42)

    def fit(self, X: pd.DataFrame):
        self.model.fit(X)

    def predict_anomaly_score(self, X: pd.DataFrame) -> np.ndarray:
        # Negative decision function values correspond to anomalies
        scores = -self.model.decision_function(X)
        # Normalize to 0-1
        min_s, max_s = scores.min(), scores.max()
        if max_s - min_s > 0:
            return (scores - min_s) / (max_s - min_s)
        return np.zeros(len(X))