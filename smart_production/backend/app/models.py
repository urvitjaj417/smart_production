"""
SQLAlchemy ORM models — the real schema for the Postgres database.

This replaces the in-browser genSim()/DATA array from the HTML prototype:
sensor readings, machines, faults, alerts, and maintenance actions now
live in actual tables instead of a JS array.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g. "M1_CNC_Mill"
    display_name = Column(String(100), nullable=False)
    machine_type = Column(String(50))  # CNC, Lathe, Press, Conveyor, Drill...
    location = Column(String(100))
    rated_output_rate = Column(Float, default=180.0)  # units/hour at 100% performance, used for OEE
    installed_at = Column(DateTime, default=datetime.utcnow)

    readings = relationship("SensorReading", back_populates="machine")
    alerts = relationship("Alert", back_populates="machine")
    maintenance_logs = relationship("MaintenanceLog", back_populates="machine")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)

    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    operating_time = Column(Float, nullable=False)   # hours
    output_rate = Column(Float, nullable=False)       # units/hour

    fault_flag = Column(Boolean, default=False, index=True)
    fault_type = Column(String(100), default="None")
    ml_risk_score = Column(Float, default=0.0)  # written by the ML prediction service

    machine = relationship("Machine", back_populates="readings")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(String(10))  # 'r' critical / 'o' warning / 'g' info
    message = Column(Text, nullable=False)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)

    machine = relationship("Machine", back_populates="alerts")


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    performed_at = Column(DateTime, default=datetime.utcnow)
    action_type = Column(String(50))  # 'preventive' | 'reactive' | 'inspection'
    description = Column(Text)
    downtime_hours = Column(Float, default=0.0)
    technician = Column(String(100))

    machine = relationship("Machine", back_populates="maintenance_logs")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True)
    description = Column(String(200))
    on_hand = Column(Integer, default=0)
    reserved = Column(Integer, default=0)


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))
    category = Column(String(100))
    on_time_pct = Column(Float, default=0.0)
    quality_score = Column(String(10))


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    item = Column(String(150))
    qty = Column(Integer)
    status = Column(String(20))  # 'g' on-time / 'o' awaiting / 'r' delayed
    expected_date = Column(DateTime, nullable=True)
