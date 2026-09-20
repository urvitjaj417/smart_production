# ml/optimizer.py
# Bottleneck detection, OEE, and workflow suggestions.

import numpy as np
import pandas as pd
from data_loader import load_data, engineer_features, summary_stats


def detect_bottlenecks(df: pd.DataFrame, fault_threshold: float = 15.0) -> pd.DataFrame:
    stats    = summary_stats(df)
    mean_out = stats["avg_output"].mean()
    std_out  = stats["avg_output"].std() + 1e-6
    stats["output_deviation"] = (stats["avg_output"] - mean_out) / std_out
    stats["is_bottleneck"]    = (
        (stats["fault_rate_pct"] >= fault_threshold) |
        (stats["output_deviation"] < -1.5)
    )
    return stats


def suggest_workflow(df: pd.DataFrame) -> list:
    stats      = detect_bottlenecks(df)
    bottleneck = stats[stats["is_bottleneck"]]
    normal     = stats[~stats["is_bottleneck"]]
    suggestions = []

    for _, row in bottleneck.sort_values("fault_rate_pct", ascending=False).iterrows():
        suggestions.append({
            "machine":  row["machine_name"],
            "priority": "CRITICAL" if row["fault_rate_pct"] > 20 else "HIGH",
            "reasons":  [f"fault rate {row['fault_rate_pct']}%"],
            "actions": [
                "Schedule immediate preventive maintenance",
                "Reduce load by 15% until inspected",
                "Redirect work to standby machine",
            ],
        })

    if len(normal) >= 1:
        best = normal.sort_values("avg_output", ascending=False).iloc[0]
        suggestions.append({
            "machine":  best["machine_name"],
            "priority": "INFO",
            "reasons":  [f"highest output ({best['avg_output']:.0f} uph, fault rate {best['fault_rate_pct']}%)"],
            "actions":  ["Route priority orders through this machine"],
        })

    return suggestions


def oee_report(df: pd.DataFrame) -> pd.DataFrame:
    stats = summary_stats(df)
    shift_min = 480.0
    stats["availability"] = (
        1 - (stats["fault_count"] * 10) / (stats["total_records"] * shift_min / 12)
    ).clip(0.5, 1.0)
    theoretical_max       = df["output_rate"].quantile(0.95)
    stats["performance"]  = (stats["avg_output"] / theoretical_max).clip(0, 1.0)
    stats["quality"]      = 1 - (stats["fault_rate_pct"] / 100)
    stats["oee_pct"]      = (stats["availability"] * stats["performance"] * stats["quality"] * 100).round(2)
    return stats[["machine_name", "availability", "performance", "quality", "oee_pct"]]


if __name__ == "__main__":
    df = engineer_features(load_data())
    print("=== Bottlenecks ===")
    print(detect_bottlenecks(df)[["machine_name","fault_rate_pct","avg_output","is_bottleneck"]].to_string(index=False))
    print("\n=== OEE ===")
    print(oee_report(df).to_string(index=False))
    print("\n=== Suggestions ===")
    for s in suggest_workflow(df):
        print(f"[{s['priority']}] {s['machine']}: {s['reasons']}")
