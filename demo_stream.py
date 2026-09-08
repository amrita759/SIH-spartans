"""
demo_stream.py
Live Interactive Demonstration Stream for SIH 2026 Problem Statement SIH26184:
Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash Withdrawal Locations in Advance.

Runs 8-10 diverse cybercrime complaint scenarios in real time:
- Step 1: Complaint Intake & Snapshot at T
- Step 2: Predictive Location Intelligence (LightGBM v2.0.0 + TreeSHAP)
- Step 3: Actionable LEA Alert & Urgency Window
- Step 4: Ground Truth Resolution & Outcome Logging (Closed Feedback Loop)
- Step 5: Multi-Case Aggregated Risk GIS Summary

Can run directly via in-process FastAPI TestClient or against a live running server.
Usage:
    python demo_stream.py
    python demo_stream.py --url http://127.0.0.1:8000 --delay 2.0
"""

import os
import sys
import time
import json
import argparse
from typing import Dict, Any, List

# Ensure project root in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def create_client(base_url: str = None):
    """Creates either an HTTP client or an in-process FastAPI TestClient."""
    if base_url:
        import requests
        try:
            r = requests.get(f"{base_url.rstrip('/')}/api/v1/health", timeout=2.0)
            if r.status_code == 200:
                print(f"[+] Connected to live backend at {base_url}")
                return ("http", requests.Session(), base_url.rstrip("/"))
        except Exception:
            print(f"[!] Could not connect to live backend at {base_url}. Falling back to in-process engine...")
    
    # Fallback to in-process TestClient
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.db.repository import init_db
    print("[*] Initializing in-process high-performance engine...")
    init_db()
    return ("in_process", TestClient(app), "")

def execute_request(client_tuple, method: str, path: str, json_data: Dict = None, params: Dict = None):
    mode, client, base_url = client_tuple
    full_url = f"{base_url}{path}" if mode == "http" else path
    
    if mode == "http":
        if method.upper() == "GET":
            return client.get(full_url, params=params).json()
        elif method.upper() == "POST":
            return client.post(full_url, json=json_data, params=params).json()
    else:
        if method.upper() == "GET":
            return client.get(full_url, params=params).json()
        elif method.upper() == "POST":
            return client.post(full_url, json=json_data, params=params).json()

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)

def format_currency(amount: float) -> str:
    return f"Rs. {amount:,.2f}"

def run_demo(client_tuple, delay_sec: float = 1.0, max_cases: int = 10):
    demo_cases_path = os.path.join(PROJECT_ROOT, "backend/app/data/demo_cases.json")
    if not os.path.exists(demo_cases_path):
        print(f"[-] Demo cases file not found: {demo_cases_path}")
        return

    with open(demo_cases_path, "r", encoding="utf-8") as f:
        cases = json.load(f)[:max_cases]

    print_header("SIH26184: Predictive Location Intelligence Live Stream")
    print(f"Operational Demonstration Stream: {len(cases)} Diverse Fraud Complaints")
    print("Underlying Model: LightGBM v2.0.0 (30 Features + RBI Banking + NCRB Crime Context)")
    print("Explainability: Exact TreeSHAP Multi-Factor Local Attribution")
    print("-" * 80)

    stats = {
        "total": 0,
        "hit_1": 0,
        "hit_3": 0,
        "hit_5": 0,
        "hit_10": 0,
        "lead_times": []
    }

    for idx, case in enumerate(cases, 1):
        case_id = case["case_id"]
        fraud_type = case.get("fraud_type", "cyber_fraud").replace("_", " ").title()
        amount = case.get("fraud_amount", 0.0)
        state = case.get("state", "UNKNOWN")
        district = case.get("district", "UNKNOWN")
        last_act = case.get("last_known_activity", {})
        channel = last_act.get("channel", "UPI")
        gt = case.get("ground_truth", {})

        print(f"\n[STREAM EVENT {idx}/{len(cases)}] CASE INTAKE: {case_id}")
        print(f"  * Modus Operandi : {fraud_type} ({channel})")
        print(f"  * Defrauded Sum  : {format_currency(amount)}")
        print(f"  * Jurisdiction   : {district}, {state}")
        print(f"  * Complaint Time : {case.get('complaint_time')}")
        print(f"  * Forecast Snap  : {case.get('prediction_time')} (T)")

        # Run Prediction
        pred_payload = {
            "case_id": case_id,
            "prediction_time": case.get("prediction_time"),
            "prediction_window_hours": case.get("prediction_window_hours", 6),
            "top_k": 10
        }
        
        try:
            pred_res = execute_request(client_tuple, "POST", "/api/v1/predictions", json_data=pred_payload)
        except Exception as e:
            print(f"  [-] Prediction failed: {e}")
            continue

        pred_id = pred_res.get("prediction_id", "N/A")
        urgency = pred_res.get("urgency_level", "NORMAL")
        remaining_h = pred_res.get("remaining_hours", 6.0)
        locations = pred_res.get("locations", [])

        print(f"  -> Prediction ID : {pred_id}")
        print(f"  -> Urgency Level : {urgency} ({remaining_h:.1f}h remaining in window)")
        print(f"\n  TOP 5 FORECASTED CASHOUT TARGETS:")
        print(f"  {'Rank':<5} {'Location ID':<18} {'Bank / Entity':<24} {'Type':<6} {'Risk':<7} {'Band':<10} {'ML Prob':<10}")
        print("  " + "-" * 78)

        actual_loc_id = gt.get("withdrawal_location_id")
        actual_rank = None

        for loc in locations[:5]:
            rank = loc.get("rank")
            lid = loc.get("location_id")
            bank = (loc.get("bank_name") or "ATM")[:22]
            ltype = loc.get("location_type", "ATM")
            score = loc.get("risk_score", 0.0)
            level = loc.get("risk_level", "LOW")
            ml_p = loc.get("model_score", 0.0)
            factors = loc.get("top_factors", [])
            factor_summary = ", ".join([f"{f['feature']}" for f in factors[:2]])

            is_actual_marker = " [ACTUAL]" if (actual_loc_id and lid == actual_loc_id) else ""
            print(f"  #{rank:<4} {lid:<18} {bank:<24} {ltype:<6} {score:<7.1f} {level:<10} {ml_p:<10.4f}{is_actual_marker}")
            if factors:
                print(f"        Key Drivers: {factor_summary}")

        # Check all locations for actual rank
        for loc in locations:
            if actual_loc_id and loc.get("location_id") == actual_loc_id:
                actual_rank = loc.get("rank")
                break

        # Ground Truth & Closed Loop Outcome Recording
        stats["total"] += 1
        if actual_loc_id:
            lead_time = gt.get("lead_time_hours", 2.5)
            stats["lead_times"].append(lead_time)

            if actual_rank == 1:
                stats["hit_1"] += 1
            if actual_rank and actual_rank <= 3:
                stats["hit_3"] += 1
            if actual_rank and actual_rank <= 5:
                stats["hit_5"] += 1
            if actual_rank and actual_rank <= 10:
                stats["hit_10"] += 1

            hit_text = f"HIT @ Rank #{actual_rank}" if actual_rank else "CANDIDATE MISSED TOP 10"
            print(f"\n  [RESOLUTION] Actual Cashout: {actual_loc_id} | Intercept Window: {lead_time:.2f}h Lead Time | Status: {hit_text}")

            # Record outcome via POST /outcome
            outcome_payload = {
                "case_id": case_id,
                "prediction_id": pred_id,
                "actual_location_id": actual_loc_id,
                "actual_withdrawal_time": gt.get("withdrawal_time"),
                "withdrawal_occurred": True,
                "apprehended": bool(actual_rank and actual_rank <= 5),
                "rank_of_actual": actual_rank,
                "in_top_3": bool(actual_rank and actual_rank <= 3),
                "in_top_5": bool(actual_rank and actual_rank <= 5),
                "in_top_10": bool(actual_rank and actual_rank <= 10),
                "lead_time_hours": lead_time,
                "prediction_risk_score": locations[0]["risk_score"] if locations else 0.0,
                "notes": f"Demonstration stream logged outcome for {case_id}"
            }
            outcome_res = execute_request(client_tuple, "POST", "/api/v1/predictions/outcome", json_data=outcome_payload)
            print(f"  [FEEDBACK LOOP] Outcome Recorded: status={outcome_res.get('status')} message='{outcome_res.get('message')}'")

        time.sleep(delay_sec)

    # Multi-Case Aggregated Risk Summary
    print_header("Aggregated Multi-Case GIS Intelligence (/risk-locations)")
    risk_locations = execute_request(client_tuple, "GET", "/api/v1/risk-locations?limit=8")
    
    locs = risk_locations.get("locations", [])
    print(f"Found {len(locs)} high-priority locations aggregated across active cases:")
    print(f"  {'Rank':<5} {'Location ID':<18} {'Bank':<22} {'Agg Score':<10} {'Band':<10} {'Cases Linked':<14}")
    print("  " + "-" * 78)
    for r in locs:
        print(f"  #{r.get('rank', 0):<4} {r.get('location_id'):<18} {(r.get('bank') or 'N/A')[:20]:<22} {r.get('risk_score', 0):<10.1f} {r.get('risk_level', ''):<10} {r.get('case_count', 1):<14}")

    # Stream Performance Summary
    print_header("Operational Stream Performance Metrics")
    total = stats["total"]
    if total > 0:
        mean_lt = sum(stats["lead_times"]) / len(stats["lead_times"]) if stats["lead_times"] else 0.0
        print(f"  * Total Evaluated Cases   : {total}")
        print(f"  * Hit@1 Accuracy          : {stats['hit_1'] / total * 100:.1f}% ({stats['hit_1']}/{total})")
        print(f"  * Hit@3 Accuracy          : {stats['hit_3'] / total * 100:.1f}% ({stats['hit_3']}/{total})")
        print(f"  * Hit@5 Accuracy          : {stats['hit_5'] / total * 100:.1f}% ({stats['hit_5']}/{total})")
        print(f"  * Hit@10 Accuracy         : {stats['hit_10'] / total * 100:.1f}% ({stats['hit_10']}/{total})")
        print(f"  * Average Lead Time       : {mean_lt:.2f} hours in advance")
    print("=" * 80)
    print("  [SUCCESS] End-to-end stream demonstration completed successfully.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SIH26184 Live Demonstration Stream")
    parser.add_argument("--url", type=str, default=None, help="Backend URL (e.g. http://127.0.0.1:8000)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between cases in seconds (default: 1.0)")
    parser.add_argument("--max-cases", type=int, default=10, help="Number of cases to stream (default: 10)")
    args = parser.parse_args()

    client = create_client(args.url)
    run_demo(client, delay_sec=args.delay, max_cases=args.max_cases)
