# ml/model_xgb.py
# XGBoost fault prediction model (as recommended in the project guide).
# Also includes Logistic Regression for comparison -- all three models in one file.
#
# Model options (guide recommendation):
#   - Logistic Regression  → easy, fast, interpretable
#   - Random Forest        → best all-round for this problem
#   - XGBoost              → advanced, highest accuracy
#
# Usage:
#   python ml/model_xgb.py --model rf       # Random Forest (default)
#   python ml/model_xgb.py --model xgb      # XGBoost
#   python ml/model_xgb.py --model lr       # Logistic Regression
#   python ml/model_xgb.py --model all      # Train and compare all three

import sys
import pickle
import argparse
import numpy as np
from pathlib import Path

from sklearn.linear_model     import LogisticRegression
from sklearn.ensemble         import RandomForestClassifier
from sklearn.model_selection  import train_test_split
from sklearn.preprocessing    import StandardScaler
from sklearn.pipeline         import Pipeline
from sklearn.metrics          import (
    classification_report, roc_auc_score, f1_score
)
from data_loader import TARGET_COL

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[WARNING] xgboost not installed. Run: pip install xgboost")

# ── Features matching the guide's dataset columns ─────────────────────────
FEATURE_COLS = [
    "temperature",
    "pressure",
    "operating_time",
    "output_rate",
    # engineered
    "temp_press_ratio",
    "efficiency",
]
MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
DEFAULT_CSV = MODELS_DIR.parent / "data" / "sensor_data.csv"


# ── Load and prepare data ──────────────────────────────────────────────────
def load_and_prepare(csv_path: str = "data/sensor_data.csv"):
    import pandas as pd
    df = pd.read_csv(csv_path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Handle both CSV formats (C module uses _c/_mms suffixes, Python generator doesn't)
    col_map = {
        "temperature_c":   "temperature",
        "pressure_bar":    "pressure",
        "cycle_time_s":    "operating_time",
        "output_rate_uph": "output_rate",
        "fault_flag":      "failure",
    }
    df = df.rename(columns=col_map)
    if "failure" in df.columns:
        df = df.rename(columns={"failure": TARGET_COL})

    # Make sure required columns exist
    for col in ["temperature", "pressure", "operating_time", "output_rate", TARGET_COL]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found. Check your CSV format.")

    # Engineer features
    df["temp_press_ratio"] = df["temperature"] / (df["pressure"] + 1e-6)
    df["efficiency"]       = df["output_rate"] / (df["operating_time"] + 1e-6)

    X = df[FEATURE_COLS].values.astype(np.float32)
    y = df[TARGET_COL].values.astype(np.int32)

    print(f"[data] {len(df)} records | faults: {y.sum()} ({y.mean()*100:.1f}%)")
    return X, y, df


# ── Build each model ───────────────────────────────────────────────────────
def build_lr() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    LogisticRegression(class_weight="balanced", max_iter=500, random_state=42)),
    ])


def build_rf() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_leaf=4,
            class_weight="balanced", random_state=42, n_jobs=-1,
        )),
    ])


def build_xgb() -> Pipeline:
    if not XGBOOST_AVAILABLE:
        raise ImportError("Install xgboost: pip install xgboost")
    scale_pos_weight = 10  # approx ratio normal/fault for imbalance
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            use_label_encoder=False, eval_metric="logloss",
            random_state=42, n_jobs=-1,
        )),
    ])


MODEL_BUILDERS = {"lr": build_lr, "rf": build_rf, "xgb": build_xgb}
MODEL_LABELS   = {"lr": "Logistic Regression", "rf": "Random Forest", "xgb": "XGBoost"}


# ── Train and evaluate one model ───────────────────────────────────────────
def train_one(name: str, X, y) -> tuple:
    builder = MODEL_BUILDERS[name]
    pipe    = builder()

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print(f"\n{'='*55}")
    print(f"  Training: {MODEL_LABELS[name]}")
    print(f"{'='*55}")
    pipe.fit(X_tr, y_tr)

    y_pred = pipe.predict(X_te)
    y_prob = pipe.predict_proba(X_te)[:, 1]

    print(classification_report(y_te, y_pred, target_names=["Normal", "Fault"]))
    auc = roc_auc_score(y_te, y_prob)
    f1  = f1_score(y_te, y_pred)
    print(f"ROC-AUC : {auc:.4f}")
    print(f"F1 Score: {f1:.4f}")

    # Save
    MODELS_DIR.mkdir(exist_ok=True)
    save_path = MODELS_DIR / f"fault_model_{name}.pkl"
    with open(save_path, "wb") as f:
        pickle.dump(pipe, f)
    print(f"Saved -> {save_path}")

    return pipe, f1, auc


# ── Optimization logic (from the guide) ───────────────────────────────────
def optimization_decision(failure_risk: float, machine_id: str) -> str:
    """
    This is the UNIQUE part of your project (as described in the guide).
    Simple rule-based logic on top of the ML probability output.
    """
    if failure_risk > 0.7:
        return f"[{machine_id}] HIGH RISK ({failure_risk:.0%}) -- Reduce load / Maintenance required"
    elif failure_risk > 0.4:
        return f"[{machine_id}] MEDIUM RISK ({failure_risk:.0%}) -- Monitor closely / Schedule inspection"
    else:
        return f"[{machine_id}] LOW RISK ({failure_risk:.0%}) -- Normal operation. No action needed."


def run_optimization_demo(pipe, X, df) -> None:
    """Print the optimization decision for every machine's worst reading."""
    probs = pipe.predict_proba(X)[:, 1]

    print(f"\n{'='*55}")
    print("  OPTIMIZATION LOGIC OUTPUT (per machine)")
    print(f"{'='*55}")

    machine_col = "machine_name" if "machine_name" in df.columns else "machine_id"
    for mid in sorted(df[machine_col].unique()):
        mask      = df[machine_col] == mid
        worst_idx = probs[mask].argmax()
        worst_prob = probs[mask][worst_idx]
        print(optimization_decision(float(worst_prob), mid))

    # Bottleneck detection
    print(f"\n{'='*55}")
    print("  BOTTLENECK DETECTION")
    print(f"{'='*55}")
    machine_avg = {}
    for mid in sorted(df[machine_col].unique()):
        mask = df[machine_col] == mid
        machine_avg[mid] = probs[mask].mean()

    fleet_avg = np.mean(list(machine_avg.values()))
    for mid, avg_risk in sorted(machine_avg.items(), key=lambda x: -x[1]):
        bottleneck = avg_risk > fleet_avg * 1.5
        tag = "  <-- BOTTLENECK: increase capacity / suggest alternate flow" if bottleneck else ""
        print(f"  {mid:<20} avg risk: {avg_risk:.1%}{tag}")


# ── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",  default="rf",
                        choices=["lr","rf","xgb","all"],
                        help="Which model to train (default: rf)")
    parser.add_argument("--csv",    default=str(DEFAULT_CSV))
    args = parser.parse_args()

    X, y, df = load_and_prepare(args.csv)

    if args.model == "all":
        results = {}
        for name in ["lr", "rf"] + (["xgb"] if XGBOOST_AVAILABLE else []):
            pipe, f1, auc = train_one(name, X, y)
            results[name] = (f1, auc)

        print(f"\n{'='*55}")
        print("  MODEL COMPARISON SUMMARY")
        print(f"{'='*55}")
        print(f"  {'Model':<22} {'F1':>8} {'ROC-AUC':>10}")
        print(f"  {'-'*40}")
        for name, (f1, auc) in sorted(results.items(), key=lambda x: -x[1][0]):
            print(f"  {MODEL_LABELS[name]:<22} {f1:>8.4f} {auc:>10.4f}")

        # Demo optimization with best model
        best_name = max(results, key=lambda k: results[k][0])
        print(f"\nBest model: {MODEL_LABELS[best_name]}")
        best_pipe_path = MODELS_DIR / f"fault_model_{best_name}.pkl"
        with open(best_pipe_path, "rb") as f:
            best_pipe = pickle.load(f)
        run_optimization_demo(best_pipe, X, df)

    else:
        pipe, f1, auc = train_one(args.model, X, y)
        run_optimization_demo(pipe, X, df)
