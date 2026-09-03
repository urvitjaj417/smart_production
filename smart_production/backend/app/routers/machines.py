from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/machines", tags=["machines"])


@router.get("/", response_model=List[schemas.MachineOut])
def list_machines(db: Session = Depends(get_db)):
    return db.query(models.Machine).all()


@router.post("/", response_model=schemas.MachineOut, status_code=201)
def create_machine(machine: schemas.MachineCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Machine).filter_by(machine_code=machine.machine_code).first()
    if existing:
        raise HTTPException(400, f"Machine code '{machine.machine_code}' already exists")
    db_machine = models.Machine(**machine.model_dump())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine


@router.get("/{machine_id}", response_model=schemas.MachineOut)
def get_machine(machine_id: int, db: Session = Depends(get_db)):
    m = db.query(models.Machine).get(machine_id)
    if not m:
        raise HTTPException(404, "Machine not found")
    return m


@router.delete("/{machine_id}", status_code=204)
def delete_machine(machine_id: int, db: Session = Depends(get_db)):
    m = db.query(models.Machine).get(machine_id)
    if not m:
        raise HTTPException(404, "Machine not found")
    db.delete(m)
    db.commit()
