"""
src/risk/urgency.py
Computes time-aware urgency and window status based on prediction timestamp T
and configured window duration (default 6 hours).
"""

import datetime
from typing import Dict, Any, Optional
from src.risk.thresholds import DEFAULT_URGENCY_HOURS

class UrgencyTracker:
    """
    Tracks prediction window expiration and calculates dynamic operational urgency.
    Does not claim certainty; generates decision-support urgency alerts.
    """
    def __init__(self, urgency_hours: Dict[str, float] = None):
        self.urgency_hours = urgency_hours or DEFAULT_URGENCY_HOURS

    def evaluate_urgency(
        self,
        prediction_time_iso: str,
        window_hours: float = 6.0,
        current_time_iso: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines remaining hours and current urgency band:
        - > 4h: NORMAL
        - 2h to 4h: ELEVATED
        - 1h to 2h: URGENT
        - < 1h: CRITICAL_EXPIRING
        - <= 0h: EXPIRED
        """
        try:
            pred_dt = datetime.datetime.fromisoformat(prediction_time_iso.replace("Z", "+00:00"))
        except Exception:
            pred_dt = datetime.datetime.now(datetime.timezone.utc)

        if current_time_iso:
            try:
                curr_dt = datetime.datetime.fromisoformat(current_time_iso.replace("Z", "+00:00"))
            except Exception:
                curr_dt = datetime.datetime.now(datetime.timezone.utc)
        else:
            curr_dt = datetime.datetime.now(datetime.timezone.utc)

        # Make time-zone aware if needed
        if pred_dt.tzinfo is None:
            pred_dt = pred_dt.replace(tzinfo=datetime.timezone.utc)
        if curr_dt.tzinfo is None:
            curr_dt = curr_dt.replace(tzinfo=datetime.timezone.utc)

        elapsed_seconds = max(0.0, (curr_dt - pred_dt).total_seconds())
        elapsed_hours = elapsed_seconds / 3600.0
        remaining_hours = max(0.0, window_hours - elapsed_hours)

        if remaining_hours <= 0.0:
            urgency_level = "EXPIRED"
            status_message = "Prediction window closed. Outcome verification pending."
        elif remaining_hours <= self.urgency_hours["URGENT"]:
            urgency_level = "CRITICAL_EXPIRING"
            status_message = "Prediction window closing (< 1 hour remaining). Expedite field verification."
        elif remaining_hours <= self.urgency_hours["ELEVATED"]:
            urgency_level = "URGENT"
            status_message = "Elevated urgency (1-2 hours remaining). Coordinate intervention."
        elif remaining_hours <= self.urgency_hours["NORMAL"]:
            urgency_level = "ELEVATED"
            status_message = "Window active (2-4 hours remaining). Monitor candidate zones."
        else:
            urgency_level = "NORMAL"
            status_message = "Early prediction window (> 4 hours remaining). Prepare intelligence brief."

        return {
            "window_total_hours": window_hours,
            "elapsed_hours": round(elapsed_hours, 2),
            "remaining_hours": round(remaining_hours, 2),
            "urgency_level": urgency_level,
            "status_message": status_message
        }
