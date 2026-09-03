"""
Executive Dashboard KPI endpoint — computes the same 8 metrics the HTML
prototype derived client-side (Plant Status, OEE, Production Today,
Downtime, Machine Health, Active Alarms, Quality Rate, Energy Consumption),
but as real SQL aggregation over the sensor_readings/alerts tables.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

ENERGY_KWH_PER_UNIT_HOUR = 0.012  # same estimate factor used in the prototype


@router.get("/kpis", response_model=schemas.KPISummary)
def get_kpis(db: Session = Depends(get_db)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    total_readings = db.query(func.count(models.SensorReading.id)).scalar() or 0
    fault_readings = db.query(func.count(models.SensorReading.id)).filter(
        models.SensorReading.fault_flag == True  # noqa: E712
    ).scalar() or 0
    quality_rate = 100 - (fault_readings / total_readings * 100 if total_readings else 0)

    today_q = db.query(models.SensorReading).filter(models.SensorReading.timestamp >= today_start)
    today_readings = today_q.all()

    production_today = int(sum(r.output_rate / 12 for r in today_readings))  # 5-min slices → units
    downtime_today = sum(1 for r in today_readings if r.fault_flag) * (5 / 60)
    energy_today = sum(r.output_rate * r.operating_time * ENERGY_KWH_PER_UNIT_HOUR for r in today_readings)

    # Performance = each reading's output_rate against that machine's own rated_output_rate,
    # averaged across all readings (falls back to 180 units/hr if a machine has none set).
    avg_ratio = db.query(
        func.avg(models.SensorReading.output_rate / func.coalesce(models.Machine.rated_output_rate, 180.0))
    ).join(models.Machine, models.SensorReading.machine_id == models.Machine.id).scalar()

    # Simplified OEE: availability * performance * quality, using fault rate as the availability proxy
    availability = max(0.5, 1 - (fault_readings * 0.5 / max(total_readings, 1)))
    performance = min(1.0, avg_ratio or 0.0)
    oee = round(availability * performance * (quality_rate / 100) * 100, 1)

    active_alarms = db.query(func.count(models.Alert.id)).filter(
        models.Alert.acknowledged == False  # noqa: E712
    ).scalar() or 0

    machine_health_pct = round(quality_rate, 0)

    return schemas.KPISummary(
        oee=oee,
        production_today=production_today,
        downtime_hours_today=round(downtime_today, 1),
        machine_health_pct=machine_health_pct,
        active_alarms=active_alarms,
        quality_rate=round(quality_rate, 1),
        energy_kwh_today=round(energy_today, 0),
    )
