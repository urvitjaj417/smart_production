# Architecture

## System overview

```
┌─────────────────┐         HTTPS/JSON          ┌──────────────────────┐
│  React Frontend  │ ───────────────────────────▶│   FastAPI Backend     │
│  (Vercel)        │◀─────────────────────────── │   (Render/Railway)    │
└─────────────────┘                              └──────────┬────────────┘
                                                             │ SQLAlchemy
                                                             ▼
                                                  ┌──────────────────────┐
                                                  │  PostgreSQL           │
                                                  │  (managed instance)   │
                                                  └──────────────────────┘
                                                             ▲
                                                             │ trains on
                                                  ┌──────────┴────────────┐
                                                  │  ML Training Pipeline │
                                                  │  (RandomForest,       │
                                                  │   scikit-learn)       │
                                                  │  → model.joblib       │
                                                  └───────────────────────┘
```

## Request flow: new sensor reading → risk score

1. A reading (temperature, pressure, operating_time, output_rate) is POSTed
   to `/api/sensor-readings/`.
2. The endpoint calls `predict_risk()` (`app/ml/predict.py`), which loads the
   trained `model.joblib` (cached in memory after first load) and runs
   inference — a real `RandomForestClassifier.predict_proba()` call, not a
   hand-written formula.
3. The reading + computed `ml_risk_score` is persisted to `sensor_readings`.
4. If `risk_score > 0.85`, an `Alert` row is auto-created.
5. The frontend polls `/api/dashboard/kpis` and `/api/sensor-readings/` to
   render the Executive Dashboard.

## Data model (see `backend/app/models.py` for the full SQLAlchemy schema)

- `machines` — one row per physical machine
- `sensor_readings` — time-series sensor data + fault labels + ML risk score
- `alerts` — generated from high-risk readings, ack/unack workflow
- `maintenance_logs` — technician actions tied to a machine
- `inventory_items` / `vendors` / `purchase_orders` — ERP-lite tables

## ML model

Two-stage `RandomForestClassifier` (see `backend/app/ml/train_model.py`):

1. **Fault detection** — binary classifier: will this reading correspond to
   a fault? Trained with `class_weight="balanced"` since faults are rare
   events (~5-9% of readings).
2. **Fault type classification** — given a fault, which of
   `Overheating / Bearing Wear / Pressure Drop / Electrical Surge` is it?

Both are trained on `temperature, pressure, operating_time, output_rate`.
Swap `generate_synthetic_training_data()` for `load_from_db()` once enough
real labeled history exists (a few thousand rows is a reasonable minimum
before the synthetic data stops being useful).

## Why RandomForest over XGBoost/LightGBM for the reference implementation

The original spec listed all three as candidates. RandomForest was chosen
for the reference implementation because it needs no extra system
dependencies beyond scikit-learn (XGBoost/LightGBM need their own compiled
libraries), trains fast enough for the CI smoke test on every push, and its
`predict_proba` calibration is adequate for a 4-hour-old dataset. Swapping
in XGBoost or LightGBM is a drop-in change in `train_model.py` and
`predict.py` — same `.fit()`/`.predict_proba()` interface.
