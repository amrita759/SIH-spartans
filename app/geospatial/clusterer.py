import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


def detect_withdrawal_hotspots(df_withdrawals: pd.DataFrame, kms_per_radian: float = 6371.0, eps_km: float = 2.0, min_samples: int = 3) -> pd.DataFrame:
    if df_withdrawals.empty or 'latitude' not in df_withdrawals.columns or 'longitude' not in df_withdrawals.columns:
        return pd.DataFrame()

    coords = np.radians(df_withdrawals[['latitude', 'longitude']].to_numpy())
    epsilon = eps_km / kms_per_radian

    db = DBSCAN(eps=epsilon, min_samples=min_samples, metric='haversine')
    df_withdrawals['cluster_id'] = db.fit_predict(coords)

    # Filter out noise points (-1)
    clusters = df_withdrawals[df_withdrawals['cluster_id'] != -1]
    if clusters.empty:
        return pd.DataFrame()

    summary = clusters.groupby('cluster_id').agg(
        latitude=('latitude', 'mean'),
        longitude=('longitude', 'mean'),
        event_count=('withdrawal_id', 'count'),
        total_amount=('amount', 'sum')
    ).reset_index()

    # Calculate cluster risk level
    summary['risk_score'] = summary['event_count'].apply(lambda count: min(int(count * 15 + 25), 100))
    summary['risk_level'] = summary['risk_score'].apply(
        lambda score: "CRITICAL" if score >= 75 else ("HIGH" if score >= 50 else ("MEDIUM" if score >= 25 else "LOW"))
    )

    return summary