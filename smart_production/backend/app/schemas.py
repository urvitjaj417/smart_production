"""
Pydantic v2 schemas — request/response contracts for the API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MachineBase(BaseModel):
    machine_code: str
    display_name: str
    machine_type: Optional[str] = None
    location: Optional[str] = None
    rated_output_rate: float = 180.0


class MachineCreate(MachineBase):
    pass


class MachineOut(MachineBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    installed_at: datetime


class SensorReadingBase(BaseModel):
    machine_id: int
    timestamp: datetime
    temperature: float
    pressure: float
    operating_time: float
    output_rate: float
    fault_flag: bool = False
    fault_type: str = "None"


class SensorReadingCreate(SensorReadingBase):
    pass


class SensorReadingOut(SensorReadingBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ml_risk_score: float


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    machine_id: int
    created_at: datetime
    severity: str
    message: str
    acknowledged: bool


class MaintenanceLogCreate(BaseModel):
    machine_id: int
    action_type: str
    description: Optional[str] = None
    downtime_hours: float = 0.0
    technician: Optional[str] = None


class MaintenanceLogOut(MaintenanceLogCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    performed_at: datetime


class PredictionRequest(BaseModel):
    """Live features sent to the trained model for a risk-score prediction."""
    temperature: float
    pressure: float
    operating_time: float
    output_rate: float


class PredictionResponse(BaseModel):
    risk_score: float
    risk_label: str  # 'low' | 'medium' | 'high'
    predicted_fault_type: Optional[str] = None


class KPISummary(BaseModel):
    oee: float
    production_today: int
    downtime_hours_today: float
    machine_health_pct: float
    active_alarms: int
    quality_rate: float
    energy_kwh_today: float
