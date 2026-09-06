import pandas as pd
import numpy as np


def extract_spatial_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if 'latitude' in df.columns and 'longitude' in df.columns:
        df['lat_rad'] = np.radians(df['latitude'])
        df['lng_rad'] = np.radians(df['longitude'])
        
    if 'hour' not in df.columns and 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['hour'] = df['datetime'].dt.hour
        df['dayofweek'] = df['datetime'].dt.dayofweek

    df['is_night_time'] = df['hour'].apply(lambda h: 1 if (h >= 22 or h <= 5) else 0)
    return df