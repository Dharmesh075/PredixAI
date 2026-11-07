"""
Analytics and Fleet Intelligence Endpoints for PredixAI.
Provides High-Level KPIs, Failure Trends, and Model Performance Metrics.
"""

import os
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.connection import get_db
from ..database.schemas import Machine, Alert, MaintenanceRecord

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

EXP_DIR = os.getenv(
    "EXPERIMENTS_DIR",
    r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\ml\experiments"
)


@router.get("")
def get_fleet_analytics(db: Session = Depends(get_db)):
    """Retrieve plant-wide fleet KPIs, health distribution, and alert summary."""
    total_machines = db.query(Machine).count()
    healthy_count = db.query(Machine).filter(Machine.health_score >= 80).count()
    warning_count = db.query(Machine).filter(Machine.health_score >= 40, Machine.health_score < 80).count()
    critical_count = db.query(Machine).filter(Machine.health_score < 40).count()

    avg_health = db.query(func.avg(Machine.health_score)).scalar() or 95.0
    avg_rul = db.query(func.avg(Machine.predicted_rul)).scalar() or 130.0

    active_alerts = db.query(Alert).filter(Alert.is_acknowledged == False).count()
    critical_alerts = db.query(Alert).filter(Alert.severity == "Critical", Alert.is_acknowledged == False).count()

    scheduled_maintenance = db.query(MaintenanceRecord).filter(MaintenanceRecord.status == "Scheduled").count()

    # Load offline ML benchmark results if available
    benchmarks = {}
    clf_path = os.path.join(EXP_DIR, 'FD001_classification_benchmarks.json')
    rul_path = os.path.join(EXP_DIR, 'FD001_rul_regression_benchmarks.json')
    shap_path = os.path.join(EXP_DIR, 'shap_global_importance.json')

    if os.path.exists(clf_path):
        with open(clf_path, 'r') as f:
            benchmarks['classification'] = json.load(f)
    if os.path.exists(rul_path):
        with open(rul_path, 'r') as f:
            benchmarks['regression'] = json.load(f)
    if os.path.exists(shap_path):
        with open(shap_path, 'r') as f:
            benchmarks['shap_importance'] = json.load(f)

    return {
        "kpis": {
            "total_machines": total_machines,
            "healthy_machines": healthy_count,
            "warning_machines": warning_count,
            "critical_machines": critical_count,
            "fleet_health_score": round(float(avg_health), 1),
            "fleet_average_rul": round(float(avg_rul), 1),
            "active_alerts": active_alerts,
            "critical_alerts": critical_alerts,
            "scheduled_maintenance_orders": scheduled_maintenance
        },
        "health_distribution": [
            {"name": "Healthy (>80%)", "value": healthy_count, "color": "#10B981"},
            {"name": "Warning (40-80%)", "value": warning_count, "color": "#F59E0B"},
            {"name": "Critical (<40%)", "value": critical_count, "color": "#EF4444"}
        ],
        "model_benchmarks": benchmarks
    }
