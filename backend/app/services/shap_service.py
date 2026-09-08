"""
backend/app/services/shap_service.py
TreeSHAP explainability service converting mathematical feature contributions
into actionable law enforcement intelligence factors.
"""

from typing import List, Dict, Any

class SHAPService:
    @staticmethod
    def format_explanations(raw_factors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardizes explanation factors into user-facing schema.
        Maps 'INCREASES_RISK' / 'DECREASES_RISK' to clean impact & direction.
        """
        formatted = []
        for f in raw_factors:
            contrib = float(f.get("contribution", 0.0))
            direction = "increases_risk" if contrib > 0 else "decreases_risk"
            formatted.append({
                "feature": f.get("feature", ""),
                "contribution": contrib,
                "impact": abs(contrib),
                "direction": direction,
                "description": f.get("description", f"Factor attribution: {f.get('feature')}")
            })
        return formatted
