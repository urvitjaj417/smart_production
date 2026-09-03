"""
Trains a real predictive-maintenance model — replaces the HTML prototype's
rule-based ml_prob formula (a hand-written function of temperature/pressure)
with an actual scikit-learn classifier trained on labeled data.

Run:
    python -m app.ml.train_model

Produces:
    app/ml/model.joblib        — trained RandomForestClassifier
    app/ml/label_encoder.joblib — encodes fault_type strings <-> ints

In production you'd train this on your real historical sensor_readings
table (see load_from_db() below) instead of synthetic data. Synthetic
data is used here so the model is trainable/demoable without a live DB.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib
import os

FAULT_TYPES = ["None", "Overheating", "Bearing Wear", "Pressure Drop", "Electrical Surge"]
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "label_encoder.joblib")


def generate_synthetic_training_data(n=20000, seed=42):
    """
    Synthetic data generator that encodes the same physical relationships
    as the original prototype's genSim(): faults correlate with elevated
    temperature/pressure and reduced output — but with real noise and
    class overlap, unlike the prototype's simple probability formula.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        base_temp = rng.normal(75, 15)
        base_pressure = rng.normal(6, 2)
        operating_time = rng.uniform(1, 24)
        output_rate = rng.normal(150, 40)

        # Fault probability rises with temperature/pressure extremes and long runtime
        risk = (
            0.15 * max(0, (base_temp - 90) / 40)
            + 0.15 * max(0, (base_pressure - 9) / 6)
            + 0.10 * (operating_time / 24)
            + rng.normal(0, 0.05)
        )
        risk = np.clip(risk, 0, 1)
        is_fault = rng.random() < risk

        if is_fault:
            fault_type = rng.choice(FAULT_TYPES[1:], p=[0.35, 0.3, 0.2, 0.15])
            # Faulty readings skew hotter/higher-pressure
            temperature = base_temp + rng.normal(15, 5)
            pressure = base_pressure + rng.normal(2, 1)
            output_rate = output_rate * rng.uniform(0.5, 0.85)
        else:
            fault_type = "None"
            temperature = base_temp
            pressure = base_pressure

        rows.append({
            "temperature": round(float(np.clip(temperature, 20, 180)), 2),
            "pressure": round(float(np.clip(pressure, 0.5, 18)), 3),
            "operating_time": round(float(operating_time), 2),
            "output_rate": round(float(np.clip(output_rate, 5, 280)), 2),
            "fault_flag": int(is_fault),
            "fault_type": fault_type,
        })
    return pd.DataFrame(rows)


def load_from_db():
    """
    Real-data path: pull labeled history straight from Postgres instead of
    synthetic data. Swap this in once you have enough real fault history
    logged (a few thousand labeled readings is a reasonable minimum).
    """
    from ..database import SessionLocal
    from .. import models
    db = SessionLocal()
    try:
        rows = db.query(models.SensorReading).all()
        return pd.DataFrame([{
            "temperature": r.temperature, "pressure": r.pressure,
            "operating_time": r.operating_time, "output_rate": r.output_rate,
            "fault_flag": int(r.fault_flag), "fault_type": r.fault_type,
        } for r in rows])
    finally:
        db.close()


def train(use_db: bool = False):
    df = load_from_db() if use_db else generate_synthetic_training_data()
    print(f"Training on {len(df)} rows ({'real DB data' if use_db else 'synthetic data'})")

    X = df[["temperature", "pressure", "operating_time", "output_rate"]]
    y_fault = df["fault_flag"]

    le = LabelEncoder()
    y_type = le.fit_transform(df["fault_type"])

    X_train, X_test, yf_train, yf_test, yt_train, yt_test = train_test_split(
        X, y_fault, y_type, test_size=0.2, random_state=42, stratify=y_fault
    )

    # Two-stage model: (1) fault yes/no, (2) fault type if yes
    clf_fault = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, class_weight="balanced")
    clf_fault.fit(X_train, yf_train)
    print("\n=== Fault detection report ===")
    print(classification_report(yf_test, clf_fault.predict(X_test)))

    clf_type = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    clf_type.fit(X_train, yt_train)
    print("=== Fault type report ===")
    print(classification_report(yt_test, clf_type.predict(X_test), zero_division=0))

    joblib.dump({"fault_model": clf_fault, "type_model": clf_type}, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)
    print(f"\nSaved model -> {MODEL_PATH}")
    print(f"Saved label encoder -> {ENCODER_PATH}")


if __name__ == "__main__":
    train(use_db=False)
