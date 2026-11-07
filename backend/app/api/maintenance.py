"""
Maintenance Scheduling and History Endpoints for PredixAI.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.schemas import MaintenanceRecord, Machine
from ..models.domain import MaintenanceResponse, MaintenanceCreate

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance"])


@router.get("", response_model=List[MaintenanceResponse])
def get_maintenance_records(
    machine_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve maintenance work orders and inspection history."""
    query = db.query(MaintenanceRecord)
    if machine_id:
        query = query.filter(MaintenanceRecord.machine_id == machine_id)
    if status:
        query = query.filter(MaintenanceRecord.status == status)

    records = query.order_by(MaintenanceRecord.scheduled_date.desc()).all()
    return records


@router.post("", response_model=MaintenanceResponse)
def schedule_maintenance(payload: MaintenanceCreate, db: Session = Depends(get_db)):
    """Schedule a preventive maintenance or overhaul order."""
    machine = db.query(Machine).filter(Machine.machine_id == payload.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    rec = MaintenanceRecord(
        machine_id=payload.machine_id,
        maintenance_type=payload.maintenance_type,
        status="Scheduled",
        scheduled_date=payload.scheduled_date,
        technician=payload.technician,
        downtime_hours=payload.downtime_hours,
        notes=payload.notes,
        created_at=datetime.utcnow()
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.patch("/{record_id}/status")
def update_maintenance_status(record_id: int, new_status: str, db: Session = Depends(get_db)):
    """Update status of maintenance (Scheduled, In Progress, Completed)."""
    rec = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")

    rec.status = new_status
    if new_status == "Completed":
        rec.completed_date = datetime.utcnow()
        # Optionally restore machine health to 100%
        machine = db.query(Machine).filter(Machine.machine_id == rec.machine_id).first()
        if machine:
            machine.health_score = 98.0
            machine.status = "Active"
            machine.failure_probability = 0.02
            machine.predicted_rul = 150.0

    db.commit()
    return {"message": f"Maintenance record {record_id} updated to {new_status}"}
