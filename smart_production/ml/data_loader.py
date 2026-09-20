# ml/data_loader.py
# Works with both data sources:
#   - generate_data.py (Python generator) -> columns: temperature, pressure, operating_time, output_rate, failure
#   - sensor_sim.c     (C generator)      -> columns: temperature_c, vibration_mms, pressure_bar, current_a, etc.

import pandas as pd
import numpy as np
from pathlib import Path

# These are the normalised column names used everywhere internally
FEATURE_COLS = [
    "temperature",
    "pressure",
    "operating_time",
    "output_rate",
    # engineered
    "temp_press_ratio",
    "efficiency",
]

TARGET_COL = "fault_flag"


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_data(csv_path: str | Path | None = None) -> pd.DataFrame:
    path = PROJECT_ROOT / "data" / "sensor_data.csv" if csv_path is None else Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(
            f"CSV not found at '{csv_path}'.\n"
            "Fix: run  python generate_data.py  first."
        )

    df = pd.read_csv(path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp").reset_index(drop=True)

    # ── Normalise column names regardless of which generator was used ──
    col_map = {
        # C module names  ->  standard names
        "temperature_c":   "temperature",
        "pressure_bar":    "pressure",
        "cycle_time_s":    "operating_time",
        "output_rate_uph": "output_rate",
        "current_a":       "current",
        "vibration_mms":   "vibration",
        # Python generator: 'failure' -> the internal target name
        "failure":         "fault_flag",
        # C generator already emits the internal target name.
        "fault_flag":      "fault_flag",
    }
    df = df.rename(columns=col_map)

    # Ensure fault_flag exists
    if "fault_flag" not in df.columns:
        raise ValueError("Could not find a failure/fault column in the CSV.")

    # Ensure machine_name exists (Python generator uses machine_id only).
    if "machine_name" not in df.columns:
        if "machine_id" not in df.columns:
            raise ValueError("CSV must contain either 'machine_name' or 'machine_id'.")
        df["machine_name"] = df["machine_id"]

    print(f"[data_loader] {len(df)} records | "
          f"faults: {int(df['fault_flag'].sum())} ({df['fault_flag'].mean()*100:.1f}%)")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["temp_press_ratio"] = df["temperature"] / (df["pressure"] + 1e-6)
    df["efficiency"]       = df["output_rate"] / (df["operating_time"] + 1e-6)

    # Rolling z-score of temperature per machine (flags gradual drift)
    df["temp_zscore"] = 0.0
    for mid in df["machine_name"].unique():
        mask = df["machine_name"] == mid
        rm   = df.loc[mask, "temperature"].rolling(50, min_periods=5).mean()
        rs   = df.loc[mask, "temperature"].rolling(50, min_periods=5).std().fillna(1.0)
        df.loc[mask, "temp_zscore"] = ((df.loc[mask, "temperature"] - rm) / rs).fillna(0)

    return df


def get_xy(df: pd.DataFrame):
    df = engineer_features(df)
    X  = df[FEATURE_COLS].values.astype(np.float32)
    y  = df[TARGET_COL].values.astype(np.int32)
    return X, y, df


def summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("machine_name").agg(
        total_records  = ("fault_flag", "count"),
        fault_count    = ("fault_flag", "sum"),
        fault_rate_pct = ("fault_flag", lambda x: round(x.mean() * 100, 2)),
        avg_temp       = ("temperature", "mean"),
        avg_output     = ("output_rate", "mean"),
    ).reset_index().round(2)


if __name__ == "__main__":
    df = load_data()
    X, y, _ = get_xy(df)
    print(f"Feature matrix: {X.shape}")
    print(summary_stats(df).to_string())
