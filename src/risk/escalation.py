"""
src/risk/escalation.py
Handles decision-support alert escalation and priority ranking.
Strictly generates predictive risk intelligence for law enforcement and banking partners.
Does not perform criminal attribution or punitive automation.
"""

from typing import Dict, Any, Optional
from src.risk.thresholds import ESCALATION_LEVELS

class EscalationManager:
    """
    Evaluates combined risk score and window urgency to determine priority level
    and generate actionable LEA operational advisory notes.
    """
    @staticmethod
    def evaluate_escalation(
        risk_score: float,
        remaining_hours: float,
        location_name: str,
        bank_name: str,
        district: str
    ) -> Dict[str, Any]:
        if risk_score >= 80.0 and remaining_hours <= 2.0:
            priority = "P1_IMMEDIATE"
        elif risk_score >= 60.0 and remaining_hours <= 4.0:
            priority = "P2_HIGH_PRIORITY"
        elif risk_score >= 40.0:
            priority = "P3_STANDARD_WATCH"
        else:
            priority = "P4_ROUTINE"

        escalation_info = ESCALATION_LEVELS[priority]

        advisory_msg = (
            f"[{priority}] Predictive cash-out intelligence: candidate '{location_name}' "
            f"({bank_name}, {district}) exhibits elevated forecast probability (Score: {risk_score:.1f}/100). "
            f"Recommended operational action: {escalation_info['action']}."
        )

        return {
            "priority": priority,
            "action_recommendation": escalation_info["action"],
            "advisory_message": advisory_msg,
            "requires_alert": priority in ["P1_IMMEDIATE", "P2_HIGH_PRIORITY"]
        }
