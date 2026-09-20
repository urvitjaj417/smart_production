# ml/model.py  (kept for backward compatibility -- use model_xgb.py instead)
import pickle, sys, numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, f1_score, roc_auc_score
from data_loader import load_data, get_xy, engineer_features, FEATURE_COLS, TARGET_COL

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "fault_model.pkl"

def rule_based_predict(df):
    flags = np.zeros(len(df), dtype=int)
    flags |= (df["temperature"]  > 110).astype(int)
    flags |= (df["pressure"]     < 2.0).astype(int)
    flags |= (df["output_rate"]  < 40.0).astype(int)
    return flags

def load_model():
    # Try both model paths
    for p in [PROJECT_ROOT / "models" / "fault_model_rf.pkl", MODEL_PATH]:
        if p.exists():
            with open(p,"rb") as f: return pickle.load(f)
    raise FileNotFoundError("No model found. Run: python ml/model_xgb.py --model rf --csv data/sensor_data.csv")

def predict_live(readings: dict) -> dict:
    pipe = load_model()
    r = readings.copy()
    aliases = {
        "temperature_c": "temperature",
        "pressure_bar": "pressure",
        "cycle_time_s": "operating_time",
        "output_rate_uph": "output_rate",
    }
    for source, target in aliases.items():
        if target not in r and source in r:
            r[target] = r[source]
    missing = [c for c in ("temperature", "pressure", "operating_time", "output_rate") if c not in r]
    if missing:
        raise ValueError(f"Missing model inputs: {missing}")
    r.setdefault("temp_press_ratio", r["temperature"] / (r["pressure"] + 1e-6))
    r.setdefault("efficiency",       r["output_rate"] / (r["operating_time"] + 1e-6))
    r.setdefault("temp_zscore", 0.0)
    X    = np.array([[r[c] for c in FEATURE_COLS]], dtype=np.float32)
    prob = float(pipe.predict_proba(X)[0][1])
    rule = r["temperature"] > 110 or r["pressure"] < 2.0 or r["output_rate"] < 40
    if rule and prob < 0.5: prob = max(prob, 0.65)
    pred = int(prob >= 0.5)
    fault_type = "None"
    if pred:
        if r["temperature"] > 110:  fault_type = "Overheating"
        elif r["pressure"]  < 2.0:  fault_type = "Pressure Drop"
        elif r["output_rate"]< 40:  fault_type = "Low Output"
        else:                        fault_type = "Unknown Anomaly"
    return {
        "fault_predicted":   pred,
        "fault_probability": round(prob, 4),
        "fault_type":        fault_type,
        "risk_level":        "HIGH" if prob>0.7 else "MEDIUM" if prob>0.4 else "LOW",
    }

if __name__ == "__main__":
    df = engineer_features(load_data())
    X, y, _ = get_xy(df)
    X_tr,X_te,y_tr,y_te = train_test_split(X,y,test_size=0.2,stratify=y,random_state=42)
    pipe = Pipeline([("sc",StandardScaler()),("clf",RandomForestClassifier(n_estimators=200,class_weight="balanced",random_state=42,n_jobs=-1))])
    pipe.fit(X_tr,y_tr)
    y_pred = pipe.predict(X_te)
    print(classification_report(y_te,y_pred,target_names=["Normal","Fault"]))
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH,"wb") as f: pickle.dump(pipe,f)
    print(f"Saved -> {MODEL_PATH}")
