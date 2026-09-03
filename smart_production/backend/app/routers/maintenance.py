from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("/", response_model=List[schemas.MaintenanceLogOut])
def list_logs(machine_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(models.MaintenanceLog)
    if machine_id:
        q = q.filter(models.MaintenanceLog.machine_id == machine_id)
    return q.order_by(desc(models.MaintenanceLog.performed_at)).all()


@router.post("/", response_model=schemas.MaintenanceLogOut, status_code=201)
def log_maintenance(entry: schemas.MaintenanceLogCreate, db: Session = Depends(get_db)):
    db_entry = models.MaintenanceLog(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry
