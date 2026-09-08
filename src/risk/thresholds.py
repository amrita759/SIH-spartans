"""
src/risk/thresholds.py
Configurable thresholds for risk scoring, risk levels, time windows, and alert escalation.
"""

from typing import Dict, Any

# Risk Score Bands (0 - 100)
DEFAULT_RISK_THRESHOLDS = {
    "CRITICAL": 80.0,
    "HIGH": 60.0,
    "MEDIUM": 40.0,
    "LOW": 0.0
}

# Intervention Urgency Window Thresholds (remaining hours out of standard 6h window)
DEFAULT_URGENCY_HOURS = {
    "NORMAL": 4.0,       # > 4h remaining
    "ELEVATED": 2.0,     # 2h to 4h remaining
    "URGENT": 1.0,       # 1h to 2h remaining
    "CRITICAL_EXPIRING": 0.0  # < 1h remaining
}

# Priority Escalation Rules
ESCALATION_LEVELS = {
    "P1_IMMEDIATE": {"min_risk": 80.0, "max_remaining_hours": 2.0, "action": "Immediate Field Dispatch & Branch Notification"},
    "P2_HIGH_PRIORITY": {"min_risk": 60.0, "max_remaining_hours": 4.0, "action": "Priority Monitoring & ATM Patrol Alert"},
    "P3_STANDARD_WATCH": {"min_risk": 40.0, "max_remaining_hours": 6.0, "action": "Watchlist & Automated Status Verification"},
    "P4_ROUTINE": {"min_risk": 0.0, "max_remaining_hours": 6.0, "action": "Log for Pattern Analysis"}
}
