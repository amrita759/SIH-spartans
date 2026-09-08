"""
src/risk/scorer.py
Calibrates raw ML output probabilities into operational 0-100 risk scores
and maps them to categorical risk levels.
"""

from typing import Dict, Any, Union
import numpy as np
from src.risk.thresholds import DEFAULT_RISK_THRESHOLDS

class RiskScorer:
    """
    Transforms raw model probabilities P(withdrawal | T) into a calibrated 0-100 risk score.
    Applies non-linear scaling to maintain high separation among top candidates.
    """
    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or DEFAULT_RISK_THRESHOLDS

    def calculate_risk_score(self, raw_prob: float) -> float:
        """
        Converts probability (0.0 to 1.0) to calibrated 0 - 100 risk score.
        For top candidates with non-trivial probabilities (0.05 - 0.40),
        logarithmic stretch maps them into operational 50 - 95 range.
        """
        prob = max(0.0, min(1.0, float(raw_prob)))
        if prob <= 0.001:
            score = prob * 1000.0 * 2.0
        elif prob <= 0.05:
            score = 20.0 + (prob - 0.001) / (0.05 - 0.001) * 30.0
        elif prob <= 0.20:
            score = 50.0 + (prob - 0.05) / (0.20 - 0.05) * 30.0
        else:
            score = 80.0 + min(18.0, (prob - 0.20) / 0.30 * 18.0)
        
        return round(float(np.clip(score, 0.0, 98.5)), 1)

    def determine_risk_level(self, risk_score: float) -> str:
        """Categorizes 0-100 score into CRITICAL, HIGH, MEDIUM, LOW."""
        if risk_score >= self.thresholds["CRITICAL"]:
            return "CRITICAL"
        elif risk_score >= self.thresholds["HIGH"]:
            return "HIGH"
        elif risk_score >= self.thresholds["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"

    def score_candidate(self, raw_prob: float) -> Dict[str, Union[float, str]]:
        score = self.calculate_risk_score(raw_prob)
        level = self.determine_risk_level(score)
        return {
            "raw_probability": round(float(raw_prob), 5),
            "risk_score": score,
            "risk_level": level
        }
