import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "trained_models")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(MODEL_DIR, exist_ok=True)


def train_and_save_model():
    csv_path = os.path.join(DATA_DIR, "synthetic_withdrawals.csv")
    if not os.path.exists(csv_path):
        from scripts.generate_dataset import generate_synthetic_data
        generate_synthetic_data()

    df = pd.read_csv(csv_path)
    df['datetime'] = pd.to_datetime(df['withdrawal_datetime'])
    df['hour'] = df['datetime'].dt.hour
    df['dayofweek'] = df['datetime'].dt.dayofweek
    df['is_night_time'] = df['hour'].apply(lambda h: 1 if (h >= 22 or h <= 5) else 0)

    # Generate binary target (1 = fraudulent cash-out, 0 = normal withdrawal)
    np.random.seed(42)
    df['is_fraud_withdrawal'] = np.where((df['amount'] > 20000) & (df['is_night_time'] == 1), 1, 0)

    features = ['latitude', 'longitude', 'amount', 'hour', 'dayofweek', 'is_night_time']
    X = df[features]
    y = df['is_fraud_withdrawal']

    model = HistGradientBoostingClassifier(random_state=42)
    model.fit(X, y)

    model_path = os.path.join(MODEL_DIR, "cash_withdrawal_classifier.joblib")
    joblib.dump(model, model_path)
    print(f"ML Model trained and saved successfully to '{model_path}'.")


if __name__ == "__main__":
    train_and_save_model()