"""
Alert Management Endpoints for PredixAI.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.schemas import Alert
from ..models.domain import AlertResponse, AlertCreate

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
def get_alerts(
    machine_id: Optional[str] = None,
    severity: Optional[str] = None,
    is_acknowledged: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Retrieve filtered alerts."""
    query = db.query(Alert)
    if machine_id:
        query = query.filter(Alert.machine_id == machine_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    if is_acknowledged is not None:
        query = query.filter(Alert.is_acknowledged == is_acknowledged)

    alerts = query.order_by(Alert.created_at.desc()).limit(100).all()
    return alerts


@router.post("", response_model=AlertResponse)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    """Manually issue an alert for a machine."""
    alert = Alert(
        machine_id=payload.machine_id,
        severity=payload.severity,
        alert_type=payload.alert_type,
        title=payload.title,
        description=payload.description,
        recommended_action=payload.recommended_action
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as acknowledged by plant operator."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert
