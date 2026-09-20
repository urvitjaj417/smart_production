# generate_data.py
# Pure Python alternative to sensor_sim.c
# Run this if you don't have gcc installed.
#
# Usage: python generate_data.py
#        python generate_data.py --records 3000 --out data/sensor_data.csv
#
# Columns match the guide exactly:
#   Machine ID, Temperature, Pressure, Operating Time, Output Rate, Failure (0/1)

import csv
import math
import random
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# ── Machine profiles ───────────────────────────────────────────────────────
MACHINES = {
    "M1_CNC_Mill":   dict(temp=72,  press=4.5, op_time=6.2, output=110),
    "M2_Lathe":      dict(temp=85,  press=6.2, op_time=7.1, output=75),
    "M3_Press":      dict(temp=91,  press=5.8, op_time=6.8, output=92),
    "M4_Conveyor":   dict(temp=68,  press=3.9, op_time=5.5, output=130),
    "M5_Drill":      dict(temp=78,  press=5.1, op_time=6.0, output=88),
}

# A small but representative factory map used by the demo dashboard.
OPERATIONS = {
    "M1_CNC_Mill":   dict(facility="Plant 1", function="Machining", process="CNC Milling", special_process="None"),
    "M2_Lathe":      dict(facility="Plant 1", function="Machining", process="CNC Turning", special_process="None"),
    "M3_Press":      dict(facility="Plant 2", function="Forming", process="Hydraulic Press", special_process="None"),
    "M4_Conveyor":   dict(facility="Plant 2", function="Assembly", process="Material Handling", special_process="None"),
    "M5_Drill":      dict(facility="Plant 1", function="Machining", process="Drilling", special_process="None"),
}

SPECIAL_PROCESS_STEPS = [
    ("Shot Peening", "Surface Treatment"),
    ("Heat Treatment", "Heat Treatment"),
    ("Anodizing", "Chemical Processing"),
    ("Non-Destructive Testing", "Inspection"),
    ("Welding", "Joining"),
    ("Painting", "Finishing"),
]

FAULT_RATE   = 0.08   # 8% of records will be fault events
FAULT_TYPES  = ["Overheating", "Bearing Wear", "Pressure Drop", "Electrical Surge"]


def normal(mean: float, cv: float = 0.03) -> float:
    """Return a normally distributed value with given coefficient of variation."""
    stddev = mean * cv
    # Box-Muller in pure Python
    u1 = random.random() + 1e-10
    u2 = random.random()
    z  = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return mean + z * stddev


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def inject_fault(row: dict, fault_type: str) -> dict:
    """Modify sensor readings to simulate a specific fault."""
    r = row.copy()
    if fault_type == "Overheating":
        r["temperature"] *= normal(1.35, 0.04)
        r["failure"]      = 1
        r["fault_type"]   = fault_type

    elif fault_type == "Bearing Wear":
        r["operating_time"] *= normal(1.20, 0.05)   # machine slows down
        r["output_rate"]    *= normal(0.75, 0.05)
        r["failure"]         = 1
        r["fault_type"]      = fault_type

    elif fault_type == "Pressure Drop":
        r["pressure"]    *= normal(0.55, 0.06)
        r["output_rate"] *= normal(0.85, 0.04)
        r["failure"]      = 1
        r["fault_type"]   = fault_type

    elif fault_type == "Electrical Surge":
        r["temperature"] *= normal(1.18, 0.04)
        r["pressure"]    *= normal(1.25, 0.05)
        r["failure"]      = 1
        r["fault_type"]   = fault_type

    return r


def generate(num_records: int = 2000, out_path: str = "data/sensor_data.csv") -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    machine_ids = list(MACHINES.keys())
    start_time  = datetime(2023, 11, 14, 22, 0, 0)
    faults      = 0

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "machine_id",
            "facility", "function", "process", "special_process", "batch_id",
            "temperature", "pressure", "operating_time",
            "output_rate", "failure", "fault_type",
        ])
        writer.writeheader()

        for i in range(num_records):
            mid     = random.choice(machine_ids)
            profile = MACHINES[mid]
            ts      = start_time + timedelta(minutes=5 * i)

            row = {
                "timestamp":      ts.strftime("%Y-%m-%d %H:%M:%S"),
                "machine_id":     mid,
                "temperature":    round(clamp(normal(profile["temp"],   0.03), 20,  180), 2),
                "pressure":       round(clamp(normal(profile["press"],  0.04),  0.5, 18), 3),
                "operating_time": round(clamp(normal(profile["op_time"],0.04),  1.0, 24), 3),
                "output_rate":    round(clamp(normal(profile["output"], 0.05),  5,  280), 2),
                "failure":        0,
                "fault_type":     "None",
                "facility":       OPERATIONS[mid]["facility"],
                "function":        OPERATIONS[mid]["function"],
                "process":         OPERATIONS[mid]["process"],
                "special_process": "None",
                "batch_id":        f"B-{(i // 20) + 1:04d}",
            }

            # Attach a special-process step to roughly one third of production
            # records so the dashboard can demonstrate process-level monitoring.
            if random.random() < 0.34:
                row["special_process"], row["function"] = random.choice(SPECIAL_PROCESS_STEPS)

            if random.random() < FAULT_RATE:
                fault = random.choice(FAULT_TYPES)
                row   = inject_fault(row, fault)
                faults += 1

            writer.writerow(row)

    print(f"[generate_data] {num_records} records written to {out_path}")
    print(f"[generate_data] Faults injected: {faults} ({faults/num_records*100:.1f}%)")
    print(f"[generate_data] Columns: timestamp, machine_id, facility, function, process, "
          f"special_process, temperature, pressure, operating_time, output_rate, failure, fault_type")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate simulated production sensor data")
    parser.add_argument("--records", type=int, default=2000,    help="Number of records")
    parser.add_argument("--out",     type=str, default="data/sensor_data.csv", help="Output CSV path")
    args = parser.parse_args()
    generate(args.records, args.out)
