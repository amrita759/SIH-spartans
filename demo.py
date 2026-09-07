"""
demo.py - Quick End-to-End Verification Demo for SIH26184
Demonstrates an active cybercrime complaint case being scored in real-time,
ranked across candidate ATMs, and explained with TreeSHAP.
"""

import json
from api.services.prediction_service import get_prediction_service
from api.schemas import PredictRequest

def main():
    print("=" * 75)
    print(" SIH 2026 (SIH26184): PREDICTIVE CASH-WITHDRAWAL LOCATION INTELLIGENCE")
    print("=" * 75)
    
    # 1. Initialize Service
    print("\n[1] Initializing ML Prediction Service (Loading Model, ATMs & Pipeline)...")
    service = get_prediction_service()
    
    # 2. Simulated Active Cybercrime Complaint at Prediction Time T
    sample_case = PredictRequest(
        case_id="CF2026_MUM_LIVE_DEMO",
        prediction_time="2026-09-07T14:30:00",
        prediction_window_hours=6,
        complaint_time="2026-09-07T13:55:00",
        fraud_type="investment_scam",
        fraud_amount=175000.00,
        state="MAHARASHTRA",
        district="MUMBAI SUBURBAN",
        victim_latitude=19.0760,
        victim_longitude=72.8777,
        last_known_activity={
            "timestamp": "2026-09-07T14:15:00",
            "channel": "UPI",
            "amount": 75000.00,
            "recipient_account_id": "ACC_MULE_49201",
            "latitude": 19.0825,
            "longitude": 72.8850
        }
    )

    print(f"\n[2] Submitting Active Case Snapshot:")
    print(f"    - Case ID: {sample_case.case_id}")
    print(f"    - Fraud Type: {sample_case.fraud_type.upper()}")
    print(f"    - Fraud Amount: INR {sample_case.fraud_amount:,.2f}")
    print(f"    - Prediction Time T: {sample_case.prediction_time}")
    print(f"    - Prediction Window: Next {sample_case.prediction_window_hours} Hours")
    print(f"    - Last Known Activity: UPI transfer to mule account near lat={sample_case.last_known_activity.latitude}, lon={sample_case.last_known_activity.longitude}")

    # 3. Predict & Rank
    print("\n[3] Scoring & Ranking Candidate ATMs in Area...")
    response = service.predict_case(sample_case, top_k=5)

    print(f"\n[4] SUCCESS! Scored {response.total_candidates_scored} candidate ATMs.")
    print(f"    Model Version: {response.model_version}\n")
    print("-" * 75)
    print(f"{'RANK':<5} | {'ATM CODE':<18} | {'BANK':<20} | {'RISK SCORE':<10} | {'LEVEL':<10}")
    print("-" * 75)

    for pred in response.predictions:
        print(f"{pred.rank:<5} | {pred.location_id:<18} | {pred.bank_name[:19]:<20} | {pred.risk_score:<10.1f} | {pred.risk_level:<10}")
        print(f"      Coordinates: ({pred.latitude:.4f}, {pred.longitude:.4f}) in {pred.district}, {pred.state}")
        print(f"      Top Factors (SHAP Intelligence):")
        for f in pred.top_factors:
            print(f"        * [{f.impact}] {f.description} (contribution: {f.contribution:+.3f})")
        print("-" * 75)

    print("\nSystem verification complete. All components operational!\n")

if __name__ == "__main__":
    main()
