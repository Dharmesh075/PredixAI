"""
Pydantic Schemas for PredixAI API Request and Response Serialization.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# Machine Schemas
# -------------------------------------------------------------
class MachineBase(BaseModel):
    machine_id: str = Field(..., example="ENG-001")
    name: str = Field(..., example="Turbofan Engine 001")
    machine_type: str = Field(default="Turbofan Engine", example="Turbofan Engine")
    model_series: str = Field(default="C-MAPSS-9000", example="C-MAPSS-9000")
    location: str = Field(default="Facility Alpha - Cell 04", example="Facility Alpha - Cell 04")
    status: str = Field(default="Active", example="Active")


class MachineCreate(MachineBase):
    pass


class MachineResponse(MachineBase):
    id: int
    current_cycle: int
    health_score: float
    failure_probability: float
    predicted_rul: float
    anomaly_score: float
    is_anomalous: bool
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Sensor Reading Schemas
# -------------------------------------------------------------
class SensorReadingInput(BaseModel):
    machine_id: str = Field(..., example="ENG-001")
    cycle: int = Field(default=1, example=120)
    setting1: float = Field(default=0.0012, example=0.0012)
    setting2: float = Field(default=0.0003, example=0.0003)
    setting3: float = Field(default=100.0, example=100.0)
    s1: Optional[float] = 518.67
    s2: Optional[float] = 642.50
    s3: Optional[float] = 1589.20
    s4: Optional[float] = 1404.30
    s5: Optional[float] = 14.62
    s6: Optional[float] = 21.61
    s7: Optional[float] = 553.80
    s8: Optional[float] = 2388.05
    s9: Optional[float] = 9050.10
    s10: Optional[float] = 1.30
    s11: Optional[float] = 47.50
    s12: Optional[float] = 521.80
    s13: Optional[float] = 2388.08
    s14: Optional[float] = 8135.00
    s15: Optional[float] = 8.42
    s16: Optional[float] = 0.03
    s17: Optional[float] = 392.0
    s18: Optional[float] = 2388.0
    s19: Optional[float] = 100.0
    s20: Optional[float] = 38.90
    s21: Optional[float] = 23.38


class SensorReadingResponse(SensorReadingInput):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Prediction Schemas
# -------------------------------------------------------------
class ShapFactor(BaseModel):
    sensor: str
    contribution: float
    impact: str  # "Increases Risk", "Decreases Risk", "Neutral"
    description: str


class PredictionResponse(BaseModel):
    machine_id: str
    cycle: int
    failure_probability: float
    predicted_rul: float
    anomaly_score: float
    is_anomalous: bool
    risk_level: str
    health_score: float
    confidence: float
    shap_factors: List[ShapFactor]
    timestamp: datetime


# -------------------------------------------------------------
# Alert Schemas
# -------------------------------------------------------------
class AlertCreate(BaseModel):
    machine_id: str
    severity: str = "Warning"  # Critical, Warning, Info
    alert_type: str = "Degradation Warning"
    title: str
    description: str
    recommended_action: Optional[str] = None


class AlertResponse(AlertCreate):
    id: int
    is_acknowledged: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Maintenance Schemas
# -------------------------------------------------------------
class MaintenanceCreate(BaseModel):
    machine_id: str
    maintenance_type: str = "Preventive Inspection"
    scheduled_date: datetime
    technician: str = "Engineering Team"
    downtime_hours: float = 4.0
    notes: Optional[str] = ""


class MaintenanceResponse(MaintenanceCreate):
    id: int
    status: str
    completed_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Assistant Chat Schema
# -------------------------------------------------------------
class AssistantQuery(BaseModel):
    machine_id: Optional[str] = None
    query: str


class AssistantResponse(BaseModel):
    response: str
    machine_id: Optional[str] = None
    key_metrics: Optional[Dict[str, Any]] = None
    recommended_action: Optional[str] = None
