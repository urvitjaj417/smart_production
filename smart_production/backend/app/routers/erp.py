from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from .. import models
from ..database import get_db

router = APIRouter(prefix="/api/erp", tags=["erp"])


class InventoryIn(BaseModel):
    sku: str
    description: str
    on_hand: int = 0
    reserved: int = 0


class InventoryOut(InventoryIn):
    id: int
    class Config:
        from_attributes = True


class VendorIn(BaseModel):
    name: str
    category: str
    on_time_pct: float = 0.0
    quality_score: str = ""


class VendorOut(VendorIn):
    id: int
    class Config:
        from_attributes = True


class POIn(BaseModel):
    po_number: str
    vendor_id: int
    item: str
    qty: int
    status: str = "o"


class POOut(POIn):
    id: int
    class Config:
        from_attributes = True


@router.get("/inventory", response_model=List[InventoryOut])
def list_inventory(db: Session = Depends(get_db)):
    return db.query(models.InventoryItem).all()


@router.post("/inventory", response_model=InventoryOut, status_code=201)
def add_inventory(item: InventoryIn, db: Session = Depends(get_db)):
    db_item = models.InventoryItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/inventory/{item_id}", status_code=204)
def delete_inventory(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.InventoryItem).get(item_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()


@router.get("/vendors", response_model=List[VendorOut])
def list_vendors(db: Session = Depends(get_db)):
    return db.query(models.Vendor).all()


@router.post("/vendors", response_model=VendorOut, status_code=201)
def add_vendor(vendor: VendorIn, db: Session = Depends(get_db)):
    db_vendor = models.Vendor(**vendor.model_dump())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


@router.get("/purchase-orders", response_model=List[POOut])
def list_pos(db: Session = Depends(get_db)):
    return db.query(models.PurchaseOrder).all()


@router.post("/purchase-orders", response_model=POOut, status_code=201)
def add_po(po: POIn, db: Session = Depends(get_db)):
    db_po = models.PurchaseOrder(**po.model_dump())
    db.add(db_po)
    db.commit()
    db.refresh(db_po)
    return db_po
