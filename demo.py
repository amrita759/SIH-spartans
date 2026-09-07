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
        case_id="CF2026_DELHI_TEST",
        prediction_time="2026-09-07T03:30:00",  # Late night 3:30 AM
        prediction_window_hours=6,
        fraud_type="corporate_cyber_heist",  # Changed from investment scam
        fraud_amount=1200000.00,  # ₹12 Lakhs (Large corporate theft)
        state="DELHI",  # Changed from MAHARASHTRA
        district="DELHI",
        victim_latitude=28.7041,  # Delhi coordinates
        victim_longitude=77.1025,
        last_known_activity={
            "timestamp": "2026-09-07T03:15:00",
            "channel": "RTGS",
            "amount": 800000.00,
            "latitude": 28.7050,
            "longitude": 77.1030,
            },
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
