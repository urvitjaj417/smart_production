from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from .. import models, schemas
from ..database import get_db
from ..ml.predict import predict_risk

router = APIRouter(prefix="/api/sensor-readings", tags=["sensor-readings"])


@router.get("/", response_model=List[schemas.SensorReadingOut])
def list_readings(
    machine_id: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = Query(500, le=5000),
    db: Session = Depends(get_db),
):
    q = db.query(models.SensorReading)
    if machine_id:
        q = q.filter(models.SensorReading.machine_id == machine_id)
    if start:
        q = q.filter(models.SensorReading.timestamp >= start)
    if end:
        q = q.filter(models.SensorReading.timestamp <= end)
    return q.order_by(desc(models.SensorReading.timestamp)).limit(limit).all()


@router.post("/", response_model=schemas.SensorReadingOut, status_code=201)
def create_reading(reading: schemas.SensorReadingCreate, db: Session = Depends(get_db)):
    """
    Ingest a single sensor reading. Runs it through the trained ML model
    to compute a live risk score before storing (real inference — not a
    random number, replaces the HTML prototype's rn()-based fake risk).
    """
    machine = db.query(models.Machine).get(reading.machine_id)
    if not machine:
        raise HTTPException(404, "machine_id not found")

    risk = predict_risk(
        temperature=reading.temperature,
        pressure=reading.pressure,
        operating_time=reading.operating_time,
        output_rate=reading.output_rate,
    )

    db_reading = models.SensorReading(**reading.model_dump(), ml_risk_score=risk["risk_score"])
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)

    # Auto-generate an alert for high-risk readings
    if risk["risk_score"] > 0.85:
        alert = models.Alert(
            machine_id=reading.machine_id,
            severity="r",
            message=f"Critical risk detected ({risk['risk_score']*100:.1f}%) — possible {risk['risk_label']} risk fault",
        )
        db.add(alert)
        db.commit()

    return db_reading


@router.post("/bulk", status_code=201)
def bulk_ingest(readings: List[schemas.SensorReadingCreate], db: Session = Depends(get_db)):
    """Bulk-insert readings (e.g. from a CSV upload processed client-side or a batch job)."""
    count = 0
    for r in readings:
        risk = predict_risk(
            temperature=r.temperature, pressure=r.pressure,
            operating_time=r.operating_time, output_rate=r.output_rate,
        )
        db.add(models.SensorReading(**r.model_dump(), ml_risk_score=risk["risk_score"]))
        count += 1
    db.commit()
    return {"inserted": count}
