import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Coordinates around Delhi NCR hotspot clusters for realistic synthetic demonstration
CLUSTERS = [
    {"lat": 28.6139, "lng": 77.2090, "name": "Connaught Place"},
    {"lat": 28.5355, "lng": 77.3910, "name": "Noida Sector 18"},
    {"lat": 28.4595, "lng": 77.0266, "name": "Gurugram Cyber Hub"}
]


def generate_synthetic_data(num_records: int = 200):
    complaints = []
    withdrawals = []

    start_date = datetime.now() - timedelta(days=30)

    for i in range(num_records):
        cluster = random.choice(CLUSTERS)
        lat = cluster["lat"] + np.random.normal(0, 0.01)
        lng = cluster["lng"] + np.random.normal(0, 0.01)

        dt = start_date + timedelta(days=random.randint(0, 29), hours=random.randint(0, 23))

        complaints.append({
            "complaint_id": f"NCRP-2026-{10000 + i}",
            "crime_category": random.choice(["Financial Fraud", "UPI Phishing", "Identity Theft", "SIM Swap"]),
            "fraud_amount": round(random.uniform(10000, 250000), 2),
            "complaint_datetime": dt.isoformat(),
            "state": "Delhi",
            "district": "New Delhi",
            "latitude": round(lat, 5),
            "longitude": round(lng, 5)
        })

        # Generate correlated withdrawal near complaint location within short time window
        w_dt = dt + timedelta(hours=random.randint(1, 6))
        withdrawals.append({
            "withdrawal_id": f"WTH-2026-{50000 + i}",
            "atm_id": f"ATM-DEL-{random.randint(100, 999)}",
            "amount": round(random.uniform(5000, 50000), 2),
            "withdrawal_datetime": w_dt.isoformat(),
            "latitude": round(lat + np.random.normal(0, 0.002), 5),
            "longitude": round(lng + np.random.normal(0, 0.002), 5),
            "state": "Delhi",
            "district": "New Delhi"
        })

    pd.DataFrame(complaints).to_csv(os.path.join(DATA_DIR, "synthetic_complaints.csv"), index=False)
    pd.DataFrame(withdrawals).to_csv(os.path.join(DATA_DIR, "synthetic_withdrawals.csv"), index=False)
    print(f"Generated {num_records} synthetic complaints and withdrawals in 'data/' directory.")


if __name__ == "__main__":
    generate_synthetic_data()