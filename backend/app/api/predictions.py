"""
Prediction Endpoints for PredixAI.
Provides Real-Time Inference: Failure Probability, RUL, Anomaly Detection, and Full Pipeline.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..database.connection import get_db
from ..database.schemas import Machine, SensorReading, Prediction
from ..models.domain import SensorReadingInput, PredictionResponse
from ..services.prediction_service import prediction_service
from ..services.alert_service import AlertService

router = APIRouter(prefix="/api/predict", tags=["Predictions"])


@router.post("/full", response_model=PredictionResponse)
def predict_full_pipeline(reading: SensorReadingInput, db: Session = Depends(get_db)):
    """
    Ingests sensor reading, runs complete ML pipeline (Kalman smoothing, failure classification,
    RUL regression, anomaly detection, SHAP attribution), persists data, triggers alert logic,
    and updates machine health.
    """
    machine = db.query(Machine).filter(Machine.machine_id == reading.machine_id).first()
    if not machine:
        # Auto-register if not yet registered (for seamless IoT ingestion)
        machine = Machine(
            machine_id=reading.machine_id,
            name=f"Turbofan Unit {reading.machine_id}",
            machine_type="Turbofan Engine",
            location="Facility Alpha - Cell 04"
        )
        db.add(machine)
        db.commit()
        db.refresh(machine)

    sensor_dict = reading.dict()

    # Retrieve last 10 historical readings for rolling window feature calculation
    past_records = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == reading.machine_id)
        .order_by(SensorReading.cycle.desc())
        .limit(10)
        .all()
    )
    history = [
        {k: getattr(r, k) for k in sensor_dict.keys() if hasattr(r, k)}
        for r in reversed(past_records)
    ]

    # Run ML prediction pipeline
    result = prediction_service.predict(
        sensor_dict=sensor_dict,
        machine_id=reading.machine_id,
        cycle=reading.cycle,
        history=history
    )

    # Persist sensor reading
    db_reading = SensorReading(**sensor_dict)
    db.add(db_reading)

    # Persist prediction
    db_pred = Prediction(
        machine_id=reading.machine_id,
        cycle=reading.cycle,
        failure_probability=result['failure_probability'],
        predicted_rul=result['predicted_rul'],
        anomaly_score=result['anomaly_score'],
        risk_level=result['risk_level'],
        confidence=result['confidence'],
        shap_factors=result['shap_factors'],
        timestamp=datetime.utcnow()
    )
    db.add(db_pred)

    # Update machine state
    machine.current_cycle = reading.cycle
    machine.health_score = result['health_score']
    machine.failure_probability = result['failure_probability']
    machine.predicted_rul = result['predicted_rul']
    machine.anomaly_score = result['anomaly_score']
    machine.is_anomalous = result['is_anomalous']
    machine.status = result['risk_level'] if result['risk_level'] != "Normal" else "Active"
    machine.last_seen = datetime.utcnow()

    # Process automated alerts
    AlertService.process_prediction_alerts(db, machine, result)

    db.commit()
    return result


@router.post("/failure")
def predict_failure_only(reading: SensorReadingInput):
    """Predicts machine failure probability within 30 operating cycles."""
    X = prediction_service.build_feature_vector(reading.dict())
    if prediction_service.failure_clf is not None:
        probs = prediction_service.failure_clf.predict_proba(X)[0]
        prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
    else:
        prob = 0.05
    return {
        "machine_id": reading.machine_id,
        "cycle": reading.cycle,
        "failure_probability": round(prob, 4),
        "will_fail_soon": bool(prob >= 0.5)
    }


@router.post("/rul")
def predict_rul_only(reading: SensorReadingInput):
    """Estimates Remaining Useful Life (cycles remaining before failure)."""
    X = prediction_service.build_feature_vector(reading.dict())
    if prediction_service.rul_reg is not None:
        rul = float(prediction_service.rul_reg.predict(X)[0])
    else:
        rul = 120.0
    return {
        "machine_id": reading.machine_id,
        "cycle": reading.cycle,
        "predicted_rul": round(max(0.0, rul), 1),
        "status": "Safe" if rul > 35 else ("Warning" if rul > 15 else "Critical")
    }


@router.post("/anomaly")
def detect_anomaly_only(reading: SensorReadingInput):
    """Detects unusual multi-sensor patterns using calibrated Isolation Forest / Autoencoder."""
    X = prediction_service.build_feature_vector(reading.dict())
    if prediction_service.iso_forest is not None:
        raw_score = float(prediction_service.iso_forest.decision_function(X)[0])
        score = float(1.0 / (1.0 + (2.71828 ** (10.0 * raw_score))))
        is_anom = bool(raw_score < 0.0)
    else:
        score = 0.05
        is_anom = False
    return {
        "machine_id": reading.machine_id,
        "cycle": reading.cycle,
        "anomaly_score": round(score, 4),
        "is_anomalous": is_anom,
        "interpretation": "Elevated sensor deviation" if is_anom else "Nominal operating profile"
    }
