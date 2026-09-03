"""
Real-time inference service. Loads the model trained by train_model.py
and serves predictions to the /api/sensor-readings ingest endpoint.

Falls back to a simple rule-based estimate if no trained model file is
present yet (e.g. fresh clone before running `python -m app.ml.train_model`),
so the API doesn't hard-crash on first boot.
"""
import os
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "label_encoder.joblib")

_model_cache = None
_encoder_cache = None


def _load():
    global _model_cache, _encoder_cache
    if _model_cache is None and os.path.exists(MODEL_PATH):
        _model_cache = joblib.load(MODEL_PATH)
        _encoder_cache = joblib.load(ENCODER_PATH)
    return _model_cache, _encoder_cache


def predict_risk(temperature: float, pressure: float, operating_time: float, output_rate: float) -> dict:
    model, encoder = _load()
    features = np.array([[temperature, pressure, operating_time, output_rate]])

    if model is None:
        # Fallback: same rule-based estimate as the HTML prototype, used only
        # until train_model.py has been run at least once.
        risk = min(1.0, max(0.0,
            0.15 * max(0, (temperature - 90) / 40)
            + 0.15 * max(0, (pressure - 9) / 6)
            + 0.10 * (operating_time / 24)
        ))
        return {"risk_score": round(risk, 3), "risk_label": _label(risk), "predicted_fault_type": None}

    fault_proba = model["fault_model"].predict_proba(features)[0]
    risk_score = float(fault_proba[1]) if len(fault_proba) > 1 else 0.0

    predicted_type = None
    if risk_score > 0.5:
        type_pred = model["type_model"].predict(features)[0]
        predicted_type = encoder.inverse_transform([type_pred])[0]

    return {
        "risk_score": round(risk_score, 3),
        "risk_label": _label(risk_score),
        "predicted_fault_type": predicted_type,
    }


def _label(risk: float) -> str:
    if risk > 0.7:
        return "high"
    if risk > 0.4:
        return "medium"
    return "low"
