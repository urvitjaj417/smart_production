"""
One-time seed script: creates 5 machines and 30 days of synthetic sensor
history so the dashboard has data to show on a fresh install.

Run:
    python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
import random

from app.database import SessionLocal, Base, engine
from app import models
from app.ml.predict import predict_risk

MACHINES = [
    ("M1_CNC_Mill", "CNC Mill 1", "CNC"),
    ("M2_Lathe", "Lathe 1", "Lathe"),
    ("M3_Press", "Hydraulic Press 1", "Press"),
    ("M4_Conveyor", "Conveyor Line A", "Conveyor"),
    ("M5_Drill", "Drill Station 1", "Drill"),
]

FAULT_TYPES = ["Overheating", "Bearing Wear", "Pressure Drop", "Electrical Surge"]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Machine).count() > 0:
            print("Database already seeded — skipping. Delete rows manually to re-seed.")
            return

        machine_objs = []
        for code, name, mtype in MACHINES:
            m = models.Machine(
                machine_code=code, display_name=name, machine_type=mtype,
                location="Plant Floor A", rated_output_rate=round(random.uniform(160, 200), 1),
            )
            db.add(m)
            machine_objs.append(m)
        db.commit()
        for m in machine_objs:
            db.refresh(m)

        start = datetime.utcnow() - timedelta(days=30)
        count = 0
        for m in machine_objs:
            base_temp = random.uniform(60, 90)
            base_pressure = random.uniform(4, 8)
            for i in range(30 * 24 * 12):  # every 5 minutes for 30 days
                ts = start + timedelta(minutes=5 * i)
                is_fault = random.random() < 0.03
                temp = base_temp + random.gauss(0, 5) + (15 if is_fault else 0)
                pressure = base_pressure + random.gauss(0, 1) + (2 if is_fault else 0)
                op_time = random.uniform(1, 24)
                output = max(5, random.gauss(150, 30) * (0.7 if is_fault else 1))

                risk = predict_risk(temp, pressure, op_time, output)
                reading = models.SensorReading(
                    machine_id=m.id, timestamp=ts,
                    temperature=round(temp, 2), pressure=round(pressure, 3),
                    operating_time=round(op_time, 2), output_rate=round(output, 2),
                    fault_flag=is_fault,
                    fault_type=random.choice(FAULT_TYPES) if is_fault else "None",
                    ml_risk_score=risk["risk_score"],
                )
                db.add(reading)
                count += 1
                if count % 2000 == 0:
                    db.commit()
                    print(f"  ...{count} readings inserted")
        db.commit()
        print(f"Seeded {len(machine_objs)} machines and {count} sensor readings.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
