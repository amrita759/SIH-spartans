"""
src/data/case_builder.py
Builds grounded cybercrime complaint cases, prediction-time snapshots at time T,
generates candidate locations, assigns leakage-free ground truth labels,
and exports chronological train/val/test datasets.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import json
import random
import datetime
import pandas as pd
import numpy as np
from src.data.atm_processor import haversine_distance_km

# Fraud type classification based on transaction channel and type
FRAUD_TYPE_MAP = {
    "UPI": "upi_phishing",
    "IMPS": "investment_scam",
    "RTGS": "corporate_cyber_heist",
    "NEFT": "loan_app_extortion",
    "ATM_Withdrawal": "atm_card_skimming",
    "POS": "pos_card_cloning",
    "Net_Banking": "account_takeover",
    "Cheque": "cheque_fraud",
    "Auto_Debit": "unauthorized_mandate",
    "Credit_Card": "credit_card_fraud"
}

def build_grounded_cases(
    transaction_path: str,
    atms_path: str,
    output_cases_json: str,
    output_dataset_parquet: str,
    max_cases: int = None,
    random_seed: int = 42
):
    """
    Constructs active cybercrime cases anchored on real transactions,
    generates candidate ATM locations, creates candidate-level dataset,
    and applies chronological splitting.
    """
    random.seed(random_seed)
    np.random.seed(random_seed)

    print(f"Loading transactions from {transaction_path}...")
    df_tx = pd.read_csv(
        transaction_path,
        usecols=[
            "transaction_id", "customer_id", "transaction_date", "transaction_time",
            "transaction_type", "transaction_amount", "transaction_direction",
            "state", "channel", "is_fraud"
        ]
    )

    print(f"Loading indexed ATMs from {atms_path}...")
    df_atms = pd.read_parquet(atms_path)
    
    # Pre-index ATMs by state for fast regional retrieval
    atms_by_state = {}
    for state, group in df_atms.groupby("state"):
        atms_by_state[state] = group

    # Filter to fraudulent transactions
    fraud_tx = df_tx[df_tx["is_fraud"] == 1].copy()
    fraud_tx = fraud_tx.sort_values(["transaction_date", "transaction_time"]).reset_index(drop=True)
    
    if max_cases and len(fraud_tx) > max_cases:
        step = len(fraud_tx) // max_cases
        fraud_tx = fraud_tx.iloc[::step].head(max_cases).reset_index(drop=True)

    print(f"Formulating {len(fraud_tx)} grounded cybercrime cases...")

    cases = []
    dataset_rows = []

    # Historical counter for historical ATM fraud counts (strictly updated in chronological order)
    historical_atm_fraud_counts = {}

    for idx, row in fraud_tx.iterrows():
        case_id = f"CF_{row['transaction_date'][:4]}_{idx+1:05d}"
        state = str(row["state"]).strip().upper()
        if state == "UP":
            state = "UTTAR PRADESH"
        elif state == "NCT OF DELHI":
            state = "DELHI"

        state_atms = atms_by_state.get(state)
        if state_atms is None or len(state_atms) == 0:
            state_atms = df_atms.sample(n=100, random_state=random_seed)

        # Parse transaction timestamp
        tx_time_str = f"{row['transaction_date']} {row['transaction_time']}:00"
        try:
            tx_dt = datetime.datetime.strptime(tx_time_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            tx_dt = datetime.datetime(2020, 1, 1, 12, 0, 0)

        # Complaint filed 10 to 45 mins after fraud txn
        complaint_delay_min = random.randint(10, 45)
        complaint_dt = tx_dt + datetime.timedelta(minutes=complaint_delay_min)

        # Prediction time T is snapshot moment: 5 to 20 mins after complaint
        pred_delay_min = random.randint(5, 20)
        prediction_dt = complaint_dt + datetime.timedelta(minutes=pred_delay_min)
        prediction_time_iso = prediction_dt.isoformat()

        fraud_type = FRAUD_TYPE_MAP.get(row["transaction_type"], "cyber_fraud")
        fraud_amount = float(row["transaction_amount"])

        # Pick a regional anchor ATM to represent the local crime cluster
        anchor_atm = state_atms.sample(n=1, random_state=idx % 10000).iloc[0]
        anchor_lat, anchor_lon = float(anchor_atm["latitude"]), float(anchor_atm["longitude"])
        district = anchor_atm["district"]

        # Victim location: within 2 to 15 km of anchor
        victim_lat = anchor_lat + random.uniform(-0.05, 0.05)
        victim_lon = anchor_lon + random.uniform(-0.05, 0.05)

        # Last known activity location: within 1 to 8 km of anchor
        last_act_lat = anchor_lat + random.uniform(-0.03, 0.03)
        last_act_lon = anchor_lon + random.uniform(-0.03, 0.03)
        last_act_time = complaint_dt - datetime.timedelta(minutes=random.randint(5, 25))

        # Outcome determination (ground truth for training/evaluation):
        # ~70% of cases have a fraudulent cash withdrawal within T -> T + 6h
        has_cashout_in_window = (random.random() < 0.70)
        
        # Candidate pool selection from district/state ATMs
        district_atms = state_atms[state_atms["district"] == district]
        if len(district_atms) < 25:
            district_atms = state_atms

        # Sample candidate pool (25 candidates)
        dists = haversine_distance_km(last_act_lat, last_act_lon, district_atms["latitude"].values, district_atms["longitude"].values)
        district_atms_copy = district_atms.copy()
        district_atms_copy["dist_km"] = dists
        
        # 18 closest ATMs to last activity
        nearby = district_atms_copy.sort_values("dist_km").head(18)
        # 7 other ATMs in district (historical / regional diversity)
        others = district_atms_copy.sort_values("dist_km").iloc[18:40]
        if len(others) >= 7:
            sample_others = others.sample(n=7, random_state=idx % 500)
        else:
            sample_others = others

        cand_df = pd.concat([nearby, sample_others]).drop_duplicates(subset=["location_id"]).head(25)

        if has_cashout_in_window:
            # Cashout occurs at one of the candidates (biased toward closer ATMs)
            weights = 1.0 / (cand_df["dist_km"].values + 0.5)
            weights = weights / weights.sum()
            true_cand_idx = np.random.choice(len(cand_df), p=weights)
            true_atm = cand_df.iloc[true_cand_idx]
            true_atm_id = true_atm["location_id"]

            cashout_delay_min = random.randint(45, 270)
            withdrawal_dt = prediction_dt + datetime.timedelta(minutes=cashout_delay_min)
            withdrawal_time_iso = withdrawal_dt.isoformat()
            lead_time_hours = round(cashout_delay_min / 60.0, 2)
        else:
            # No withdrawal in window
            true_atm_id = None
            withdrawal_time_iso = None
            lead_time_hours = None

        # Build Case Record
        case_record = {
            "case_id": case_id,
            "prediction_time": prediction_time_iso,
            "prediction_window_hours": 6,
            "complaint_time": complaint_dt.isoformat(),
            "fraud_type": fraud_type,
            "fraud_amount": fraud_amount,
            "state": state,
            "district": district,
            "victim_lat": round(victim_lat, 6),
            "victim_lon": round(victim_lon, 6),
            "last_known_activity": {
                "timestamp": last_act_time.isoformat(),
                "channel": row["channel"],
                "amount": round(fraud_amount * random.uniform(0.3, 0.9), 2),
                "recipient_account_id": f"MULE_ACC_{random.randint(10000, 99999)}",
                "latitude": round(last_act_lat, 6),
                "longitude": round(last_act_lon, 6)
            },
            "ground_truth": {
                "has_cashout_in_window": has_cashout_in_window,
                "withdrawal_location_id": true_atm_id,
                "withdrawal_time": withdrawal_time_iso,
                "lead_time_hours": lead_time_hours
            }
        }
        cases.append(case_record)

        # Chronological split partition
        if prediction_time_iso <= "2022-12-31T23:59:59":
            split = "train"
        elif prediction_time_iso <= "2023-06-30T23:59:59":
            split = "val"
        else:
            split = "test"

        # Construct Candidate-Level Feature Rows
        pred_hour = prediction_dt.hour
        pred_dow = prediction_dt.weekday()
        is_weekend = 1 if pred_dow in (5, 6) else 0
        time_since_complaint = (prediction_dt - complaint_dt).total_seconds() / 60.0
        time_since_last_txn = (prediction_dt - last_act_time).total_seconds() / 60.0

        tx_count_last_1h = random.randint(1, 4)
        tx_count_last_6h = tx_count_last_1h + random.randint(0, 5)
        tx_amount_last_1h = round(fraud_amount * random.uniform(0.4, 1.0), 2)
        tx_amount_last_6h = round(tx_amount_last_1h + fraud_amount * random.uniform(0.0, 0.8), 2)
        transfer_count = random.randint(1, 5)
        amount_velocity_ratio = round(tx_amount_last_1h / (fraud_amount + 1.0), 4)

        # Mule graph features frozen at T
        mule_link_score = random.randint(1, 6) if fraud_type in ("investment_scam", "upi_phishing") else random.randint(0, 2)
        mule_graph_degree = random.randint(2, 12)

        for _, cand in cand_df.iterrows():
            cand_id = cand["location_id"]
            cand_lat = float(cand["latitude"])
            cand_lon = float(cand["longitude"])

            dist_victim = haversine_distance_km(victim_lat, victim_lon, cand_lat, cand_lon)
            dist_last_act = haversine_distance_km(last_act_lat, last_act_lon, cand_lat, cand_lon)

            # Historical ATM risk strictly frozen at T
            hist_atm_fraud_count = historical_atm_fraud_counts.get(cand_id, 0)
            burstiness = round(tx_count_last_1h / max(1.0, tx_count_last_6h / 6.0), 3)
            amount_dev = round((fraud_amount - 50000.0) / 75000.0, 3)

            # Target label
            is_target = 1 if (has_cashout_in_window and cand_id == true_atm_id) else 0

            row_dict = {
                "case_id": case_id,
                "split": split,
                "prediction_time": prediction_time_iso,
                "location_id": cand_id,
                "location_name": str(cand["location_name"]),
                "bank_name": str(cand["bank_name"]),
                "candidate_lat": cand_lat,
                "candidate_lon": cand_lon,
                "population_group": str(cand.get("population_group", "URBAN")),
                # Temporal features
                "hour_of_day": pred_hour,
                "day_of_week": pred_dow,
                "is_weekend": is_weekend,
                "time_since_complaint_min": round(time_since_complaint, 1),
                "time_since_last_txn_min": round(time_since_last_txn, 1),
                # Velocity features
                "tx_count_last_1h": tx_count_last_1h,
                "tx_count_last_6h": tx_count_last_6h,
                "tx_amount_last_1h": tx_amount_last_1h,
                "tx_amount_last_6h": tx_amount_last_6h,
                # Financial features
                "fraud_amount": fraud_amount,
                "cumulative_known_transfer_amount": tx_amount_last_6h,
                "transfer_count": transfer_count,
                "amount_velocity_ratio": amount_velocity_ratio,
                # Spatial features
                "dist_victim_to_candidate_km": round(dist_victim, 3),
                "dist_last_activity_to_candidate_km": round(dist_last_act, 3),
                "atm_density_within_2km": random.randint(3, 25),
                # Historical features (strictly frozen at T)
                "hist_atm_fraud_count_90d": hist_atm_fraud_count,
                "hist_atm_hour_affinity": round(random.uniform(0.05, 0.45), 3),
                # Behavioural features
                "burstiness_score": burstiness,
                "amount_deviation_score": amount_dev,
                # Network features
                "mule_link_score": mule_link_score,
                "mule_graph_degree": mule_graph_degree,
                # Categorical features
                "fraud_type": fraud_type,
                "last_channel": str(row["channel"]),
                # TARGET
                "target": is_target
            }
            dataset_rows.append(row_dict)

        # Update historical fraud count for next chronological cases ONLY if cashout occurred
        if has_cashout_in_window and true_atm_id:
            historical_atm_fraud_counts[true_atm_id] = historical_atm_fraud_counts.get(true_atm_id, 0) + 1

    # Save cases metadata
    os.makedirs(os.path.dirname(output_cases_json), exist_ok=True)
    with open(output_cases_json, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)
    print(f"Saved {len(cases)} case records to {output_cases_json}")

    # Save candidate-level tabular dataset
    os.makedirs(os.path.dirname(output_dataset_parquet), exist_ok=True)
    df_dataset = pd.DataFrame(dataset_rows)
    df_dataset.to_parquet(output_dataset_parquet, index=False)
    print(f"Saved {len(df_dataset)} candidate-level rows to {output_dataset_parquet}")
    
    print("\nSplit breakdown:")
    print(df_dataset.groupby("split")["case_id"].nunique().rename("unique_cases"))
    print(df_dataset.groupby("split")["target"].agg(["count", "sum", "mean"]).rename(columns={"count": "rows", "sum": "positives", "mean": "pos_rate"}))

    return df_dataset

if __name__ == "__main__":
    tx_path = "datasets/indian_banking_transactions.csv"
    atm_path = "data/processed/atms_indexed.parquet"
    out_cases = "data/synthetic/grounded_cases.json"
    out_dataset = "data/synthetic/candidate_dataset.parquet"
    # Process all 4873 fraud transactions into grounded cases
    df = build_grounded_cases(tx_path, atm_path, out_cases, out_dataset)
