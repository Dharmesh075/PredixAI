"""
Machine Management Endpoints for PredixAI.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.schemas import Machine, SensorReading, Alert, Prediction
from ..models.domain import MachineResponse, MachineCreate

router = APIRouter(prefix="/api/machines", tags=["Machines"])


@router.get("", response_model=List[MachineResponse])
def get_all_machines(db: Session = Depends(get_db)):
    """Retrieve all monitored industrial machines with latest health state."""
    machines = db.query(Machine).order_by(Machine.id.asc()).all()
    return machines


@router.post("", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
def register_machine(payload: MachineCreate, db: Session = Depends(get_db)):
    """Register a new machine into the fleet monitoring system."""
    existing = db.query(Machine).filter(Machine.machine_id == payload.machine_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Machine with ID '{payload.machine_id}' is already registered."
        )

    machine = Machine(
        machine_id=payload.machine_id,
        name=payload.name,
        machine_type=payload.machine_type,
        model_series=payload.model_series,
        location=payload.location,
        status=payload.status,
        health_score=100.0,
        predicted_rul=150.0,
        failure_probability=0.01,
        anomaly_score=0.02
    )
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


@router.get("/{machine_id}")
def get_machine_details(machine_id: str, db: Session = Depends(get_db)):
    """Retrieve comprehensive machine details, recent readings, and active alerts."""
    machine = db.query(Machine).filter(Machine.machine_id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found.")

    readings = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .order_by(SensorReading.cycle.desc())
        .limit(50)
        .all()
    )

    alerts = (
        db.query(Alert)
        .filter(Alert.machine_id == machine_id)
        .order_by(Alert.created_at.desc())
        .limit(10)
        .all()
    )

    latest_pred = (
        db.query(Prediction)
        .filter(Prediction.machine_id == machine_id)
        .order_by(Prediction.cycle.desc())
        .first()
    )

    return {
        "machine": {
            "id": machine.id,
            "machine_id": machine.machine_id,
            "name": machine.name,
            "machine_type": machine.machine_type,
            "model_series": machine.model_series,
            "location": machine.location,
            "status": machine.status,
            "current_cycle": machine.current_cycle,
            "health_score": machine.health_score,
            "failure_probability": machine.failure_probability,
            "predicted_rul": machine.predicted_rul,
            "anomaly_score": machine.anomaly_score,
            "is_anomalous": machine.is_anomalous,
            "last_seen": machine.last_seen
        },
        "recent_readings": [
            {
                "cycle": r.cycle,
                "timestamp": r.timestamp,
                "s2": r.s2,
                "s3": r.s3,
                "s4": r.s4,
                "s7": r.s7,
                "s8": r.s8,
                "s9": r.s9,
                "s11": r.s11,
                "s12": r.s12,
                "s14": r.s14,
                "s15": r.s15,
                "s17": r.s17,
                "s20": r.s20,
                "s21": r.s21
            }
            for r in reversed(readings)
        ],
        "active_alerts": [
            {
                "id": a.id,
                "severity": a.severity,
                "alert_type": a.alert_type,
                "title": a.title,
                "description": a.description,
                "recommended_action": a.recommended_action,
                "is_acknowledged": a.is_acknowledged,
                "created_at": a.created_at
            }
            for a in alerts
        ],
        "latest_shap_factors": latest_pred.shap_factors if latest_pred else []
    }


@router.get("/{machine_id}/health")
def get_machine_health(machine_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed health analytics breakdown for a machine."""
    machine = db.query(Machine).filter(Machine.machine_id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    return {
        "machine_id": machine.machine_id,
        "health_score": machine.health_score,
        "failure_probability": machine.failure_probability,
        "predicted_rul": machine.predicted_rul,
        "anomaly_score": machine.anomaly_score,
        "status": machine.status,
        "cycle": machine.current_cycle,
        "health_category": "Good" if machine.health_score >= 80 else ("Fair" if machine.health_score >= 50 else "Critical")
    }
