"""
SQLAlchemy ORM Schemas for PredixAI Database:
- Machine
- SensorReading
- Prediction
- Alert
- MaintenanceRecord
- ModelVersion
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .connection import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    machine_type = Column(String(50), default="Turbofan Engine")
    model_series = Column(String(50), default="C-MAPSS-9000")
    location = Column(String(100), default="Facility Alpha - Cell 04")
    status = Column(String(30), default="Active")  # Active, Maintenance, Warning, Critical, Offline

    # Latest operational state
    current_cycle = Column(Integer, default=1)
    health_score = Column(Float, default=100.0)      # 0 to 100%
    failure_probability = Column(Float, default=0.0) # 0.0 to 1.0
    predicted_rul = Column(Float, default=150.0)     # Estimated remaining cycles
    anomaly_score = Column(Float, default=0.05)      # 0.0 to 1.0
    is_anomalous = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    readings = relationship("SensorReading", back_populates="machine", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="machine", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="machine", cascade="all, delete-orphan")
    maintenance_records = relationship("MaintenanceRecord", back_populates="machine", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), index=True, nullable=False)
    cycle = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Operational settings
    setting1 = Column(Float, default=0.0)
    setting2 = Column(Float, default=0.0)
    setting3 = Column(Float, default=100.0)

    # Key sensor measurements (C-MAPSS 21 sensors mapped to industrial telemetry)
    s1 = Column(Float)   # Fan inlet temp (deg R)
    s2 = Column(Float)   # LPC outlet temp (deg R)
    s3 = Column(Float)   # HPC outlet temp (deg R)
    s4 = Column(Float)   # LPT outlet temp (deg R)
    s5 = Column(Float)   # Fan inlet pressure (psia)
    s6 = Column(Float)   # Bypass duct pressure (psia)
    s7 = Column(Float)   # HPC outlet pressure (psia)
    s8 = Column(Float)   # Physical fan speed (rpm)
    s9 = Column(Float)   # Physical core speed (rpm)
    s10 = Column(Float)  # Engine pressure ratio
    s11 = Column(Float)  # Static pressure HPC (psia)
    s12 = Column(Float)  # Fuel flow ratio (pps/psi)
    s13 = Column(Float)  # Corrected fan speed (rpm)
    s14 = Column(Float)  # Corrected core speed (rpm)
    s15 = Column(Float)  # Bypass ratio
    s16 = Column(Float)  # Burner fuel-air ratio
    s17 = Column(Float)  # Bleed enthalpy
    s18 = Column(Float)  # Demanded fan speed (rpm)
    s19 = Column(Float)  # Demanded corrected fan speed (rpm)
    s20 = Column(Float)  # HPT coolant bleed (lbm/s)
    s21 = Column(Float)  # LPT coolant bleed (lbm/s)

    machine = relationship("Machine", back_populates="readings")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), index=True, nullable=False)
    cycle = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    failure_probability = Column(Float, nullable=False)
    predicted_rul = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    risk_level = Column(String(20), default="Normal")  # Normal, Warning, Critical
    confidence = Column(Float, default=0.92)

    # SHAP explanations stored as JSON list of top contributing sensors
    shap_factors = Column(JSON, default=list)

    machine = relationship("Machine", back_populates="predictions")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), index=True, nullable=False)
    severity = Column(String(20), default="Warning")   # Critical, Warning, Info
    alert_type = Column(String(50), default="Degradation Warning")
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    recommended_action = Column(Text)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    machine = relationship("Machine", back_populates="alerts")


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), index=True, nullable=False)
    maintenance_type = Column(String(50), default="Preventive Inspection") # Preventive, Overhaul, Sensor Calibration
    status = Column(String(30), default="Scheduled") # Scheduled, In Progress, Completed, Deferred
    scheduled_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    technician = Column(String(100), default="Engineering Team")
    downtime_hours = Column(Float, default=4.0)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    machine = relationship("Machine", back_populates="maintenance_records")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False) # Classification, Regression, Anomaly
    version = Column(String(20), default="1.0.0")
    algorithm = Column(String(50), nullable=False)
    metrics_json = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
