from typing import Dict, Any


def calculate_risk_score(
    ml_probability: float,
    anomaly_score: float,
    nearby_complaints_count: int,
    withdrawal_amount: float
) -> Dict[str, Any]:
    # Weighted composite scoring engine
    comp_weight = min(nearby_complaints_count / 10.0, 1.0) * 25.0
    amount_weight = min(withdrawal_amount / 200000.0, 1.0) * 15.0
    ml_weight = ml_probability * 40.0
    anomaly_weight = anomaly_score * 20.0

    raw_score = comp_weight + amount_weight + ml_weight + anomaly_weight
    final_score = int(min(max(raw_score, 0), 100))

    if final_score >= 75:
        risk_level = "CRITICAL"
    elif final_score >= 50:
        risk_level = "HIGH"
    elif final_score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "breakdown": {
            "ml_factor": round(ml_weight, 2),
            "anomaly_factor": round(anomaly_weight, 2),
            "complaint_density_factor": round(comp_weight, 2),
            "amount_factor": round(amount_weight, 2)
        }
    }