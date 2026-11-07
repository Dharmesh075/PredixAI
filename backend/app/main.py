"""
PredixAI Backend Application Entrypoint.
High-Performance FastAPI Server with WebSockets, Real-Time Sensor Ingestion, and Predictive AI.
"""

import os
import asyncio
import json
from typing import List
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database.connection import engine, Base, SessionLocal, get_db
from .database.schemas import Machine, SensorReading, Prediction, Alert, MaintenanceRecord
from .api import machines, predictions, alerts, maintenance, analytics, assistant

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PredixAI Platform",
    description="Intelligent Predictive Maintenance & Machine Health Monitoring Platform",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(machines.router)
app.include_router(predictions.router)
app.include_router(alerts.router)
app.include_router(maintenance.router)
app.include_router(analytics.router)
app.include_router(assistant.router)


# -------------------------------------------------------------
# WebSocket Connection Manager for Real-Time Telemetry Streaming
# -------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """WebSocket stream for real-time industrial telemetry and prediction alerts."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open, receive potential control messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


# -------------------------------------------------------------
# Seed Database with Initial Industrial Fleet on Startup
# -------------------------------------------------------------
@app.on_event("startup")
def seed_initial_fleet():
    """Populates realistic demo engines across varied health stages (Healthy, Warning, Critical)."""
    db = SessionLocal()
    try:
        count = db.query(Machine).count()
        if count == 0:
            print("[INFO] Seeding initial industrial turbofan fleet...")
            sample_fleet = [
                {
                    "machine_id": "ENG-001",
                    "name": "Turbofan CFM-56 #101",
                    "model_series": "CFM-56-7B",
                    "location": "Facility Alpha - Bay 1",
                    "status": "Active",
                    "current_cycle": 45,
                    "health_score": 96.5,
                    "failure_probability": 0.03,
                    "predicted_rul": 138.0,
                    "anomaly_score": 0.04,
                    "is_anomalous": False
                },
                {
                    "machine_id": "ENG-002",
                    "name": "Turbofan CFM-56 #102",
                    "model_series": "CFM-56-7B",
                    "location": "Facility Alpha - Bay 2",
                    "status": "Active",
                    "current_cycle": 110,
                    "health_score": 78.4,
                    "failure_probability": 0.18,
                    "predicted_rul": 74.0,
                    "anomaly_score": 0.12,
                    "is_anomalous": False
                },
                {
                    "machine_id": "ENG-003",
                    "name": "GE-90 High-Bypass #203",
                    "model_series": "GE-90-115B",
                    "location": "Facility Beta - Test Cell 3",
                    "status": "Critical",
                    "current_cycle": 192,
                    "health_score": 28.2,
                    "failure_probability": 0.89,
                    "predicted_rul": 12.0,
                    "anomaly_score": 0.78,
                    "is_anomalous": True
                },
                {
                    "machine_id": "ENG-004",
                    "name": "Pratt & Whitney PW4000",
                    "model_series": "PW4098",
                    "location": "Facility Gamma - Test Stand 2",
                    "status": "Warning",
                    "current_cycle": 165,
                    "health_score": 48.0,
                    "failure_probability": 0.46,
                    "predicted_rul": 26.0,
                    "anomaly_score": 0.35,
                    "is_anomalous": True
                },
                {
                    "machine_id": "ENG-005",
                    "name": "Rolls-Royce Trent 1000",
                    "model_series": "Trent-1000-TEN",
                    "location": "Facility Alpha - Bay 3",
                    "status": "Active",
                    "current_cycle": 80,
                    "health_score": 88.0,
                    "failure_probability": 0.08,
                    "predicted_rul": 95.0,
                    "anomaly_score": 0.07,
                    "is_anomalous": False
                },
                {
                    "machine_id": "ENG-006",
                    "name": "Safran Silvercrest #06",
                    "model_series": "SC-2D",
                    "location": "Facility Beta - Bay 1",
                    "status": "Active",
                    "current_cycle": 20,
                    "health_score": 99.0,
                    "failure_probability": 0.01,
                    "predicted_rul": 150.0,
                    "anomaly_score": 0.02,
                    "is_anomalous": False
                }
            ]

            for m_data in sample_fleet:
                machine = Machine(**m_data)
                db.add(machine)

            db.commit()

            # Seed realistic alerts for the critical/warning machines
            crit_alert = Alert(
                machine_id="ENG-003",
                severity="Critical",
                alert_type="Imminent Failure Risk",
                title="Critical HPC Degradation: ENG-003 Estimated RUL < 15 Cycles",
                description="HPC Static Pressure (s11) and LPT outlet temp (s4) exhibit acute thermal divergence. Failure probability has reached 89%.",
                recommended_action="Emergency shutdown and dispatch borescope inspection crew to Facility Beta - Test Cell 3.",
                is_acknowledged=False,
                created_at=datetime.utcnow() - timedelta(minutes=45)
            )
            warn_alert = Alert(
                machine_id="ENG-004",
                severity="Warning",
                alert_type="Degradation Warning",
                title="Warning: High Wear Rate Detected on ENG-004",
                description="Bypass ratio and fuel flow ratio trending above baseline threshold. RUL estimated at 26 operating cycles.",
                recommended_action="Schedule blade inspection and coolant line check during next shift.",
                is_acknowledged=False,
                created_at=datetime.utcnow() - timedelta(hours=2)
            )
            db.add(crit_alert)
            db.add(warn_alert)

            # Seed upcoming maintenance
            maint1 = MaintenanceRecord(
                machine_id="ENG-003",
                maintenance_type="Compressor Overhaul",
                status="Scheduled",
                scheduled_date=datetime.utcnow() + timedelta(hours=6),
                technician="Rapid Response Team Delta",
                downtime_hours=8.0,
                notes="Priority emergency repair based on PredixAI ML prognostics."
            )
            maint2 = MaintenanceRecord(
                machine_id="ENG-004",
                maintenance_type="Preventive Inspection",
                status="Scheduled",
                scheduled_date=datetime.utcnow() + timedelta(days=2),
                technician="Diagnostics Lead Marcus V.",
                downtime_hours=4.0,
                notes="Stage 3 seal replacement and sensor recalibration."
            )
            db.add(maint1)
            db.add(maint2)

            db.commit()
            print("[SUCCESS] Initial industrial fleet, alerts, and maintenance records seeded.")
    finally:
        db.close()


@app.get("/")
def health_check():
    return {
        "status": "online",
        "platform": "PredixAI Intelligent Machine Health & Predictive Maintenance",
        "version": "2.0.0",
        "documentation": "/docs"
    }
