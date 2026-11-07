"""
Intelligent Industrial Alert Engine for PredixAI.
Evaluates prediction outputs, threshold violations, and degradation anomalies.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..database.schemas import Alert, Machine


class AlertService:
    @staticmethod
    def process_prediction_alerts(db: Session, machine: Machine, pred: Dict[str, Any]) -> Optional[Alert]:
        """
        Generates automated industrial maintenance alerts based on:
        - Critical RUL degradation (<= 15 cycles)
        - High failure probability (>= 70%)
        - Anomaly detection triggers
        """
        rul = pred.get('predicted_rul', 100.0)
        fail_prob = pred.get('failure_probability', 0.0)
        is_anomalous = pred.get('is_anomalous', False)

        alert = None

        if rul <= 15 or fail_prob >= 0.70:
            # Check if active unacknowledged critical alert already exists
            existing = db.query(Alert).filter(
                Alert.machine_id == machine.machine_id,
                Alert.severity == "Critical",
                Alert.is_acknowledged == False
            ).first()

            if not existing:
                alert = Alert(
                    machine_id=machine.machine_id,
                    severity="Critical",
                    alert_type="Imminent Failure Risk",
                    title=f"Critical RUL Alert: {machine.machine_id} Estimated Life < 15 Cycles",
                    description=(
                        f"Machine {machine.machine_id} has reached critical operational limits. "
                        f"Predicted Remaining Useful Life is {rul:.1f} cycles with failure probability {fail_prob:.1%}. "
                        f"Accelerated degradation detected in High Pressure Compressor (HPC)."
                    ),
                    recommended_action=(
                        "Immediate action required: Halt unit operations, conduct borescope inspection of HPC blades, "
                        "and dispatch maintenance crew for primary turbine overhaul."
                    ),
                    is_acknowledged=False,
                    created_at=datetime.utcnow()
                )
                db.add(alert)
                db.commit()

        elif rul <= 35 or fail_prob >= 0.35:
            existing = db.query(Alert).filter(
                Alert.machine_id == machine.machine_id,
                Alert.severity == "Warning",
                Alert.is_acknowledged == False
            ).first()

            if not existing:
                alert = Alert(
                    machine_id=machine.machine_id,
                    severity="Warning",
                    alert_type="Degradation Warning",
                    title=f"Warning: Elevated Wear Detected on {machine.machine_id}",
                    description=(
                        f"Equipment telemetry indicates non-linear wear rate. "
                        f"Predicted RUL is {rul:.1f} cycles (Failure probability: {fail_prob:.1%})."
                    ),
                    recommended_action=(
                        "Schedule preventive maintenance within next 24 operating hours. "
                        "Calibrate fuel flow ratio sensors and verify coolant bleed lines."
                    ),
                    is_acknowledged=False,
                    created_at=datetime.utcnow()
                )
                db.add(alert)
                db.commit()

        elif is_anomalous:
            existing = db.query(Alert).filter(
                Alert.machine_id == machine.machine_id,
                Alert.alert_type == "Sensor Anomaly",
                Alert.is_acknowledged == False
            ).first()

            if not existing:
                alert = Alert(
                    machine_id=machine.machine_id,
                    severity="Warning",
                    alert_type="Sensor Anomaly",
                    title=f"Sensor Telemetry Anomaly Detected on {machine.machine_id}",
                    description=(
                        f"Unsupervised anomaly detector flagged atypical sensor pattern "
                        f"with score {pred.get('anomaly_score', 0):.2f}. Divergence from baseline operating signature."
                    ),
                    recommended_action=(
                        "Inspect sensor wire harnesses, check vibration sensor calibration, and monitor upcoming cycle trends."
                    ),
                    is_acknowledged=False,
                    created_at=datetime.utcnow()
                )
                db.add(alert)
                db.commit()

        return alert
