"""
Integration and Unit Tests for PredixAI FastAPI Backend.
Verifies REST APIs, ML Inference Pipeline, Alert Generation, and Maintenance Logic.
"""

import sys
import os

# Add backend directory to path
backend_dir = r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_health():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "PredixAI" in data["platform"]


def test_get_all_machines():
    response = client.get("/api/machines")
    assert response.status_code == 200
    machines = response.json()
    assert isinstance(machines, list)
    assert len(machines) >= 6
    ids = [m["machine_id"] for m in machines]
    assert "ENG-001" in ids
    assert "ENG-003" in ids


def test_get_machine_details():
    response = client.get("/api/machines/ENG-001")
    assert response.status_code == 200
    data = response.json()
    assert "machine" in data
    assert data["machine"]["machine_id"] == "ENG-001"
    assert "recent_readings" in data
    assert "active_alerts" in data


def test_predict_full_pipeline():
    sample_payload = {
        "machine_id": "ENG-001",
        "cycle": 125,
        "setting1": -0.0007,
        "setting2": -0.0004,
        "setting3": 100.0,
        "s1": 518.67,
        "s2": 642.15,
        "s3": 1589.70,
        "s4": 1404.20,
        "s5": 14.62,
        "s6": 21.61,
        "s7": 553.80,
        "s8": 2388.06,
        "s9": 9046.19,
        "s10": 1.30,
        "s11": 47.47,
        "s12": 521.66,
        "s13": 2388.02,
        "s14": 8138.62,
        "s15": 8.4195,
        "s16": 0.03,
        "s17": 392.0,
        "s18": 2388.0,
        "s19": 100.0,
        "s20": 39.06,
        "s21": 23.4190
    }
    response = client.post("/api/predict/full", json=sample_payload)
    assert response.status_code == 200
    pred = response.json()
    assert pred["machine_id"] == "ENG-001"
    assert "failure_probability" in pred
    assert "predicted_rul" in pred
    assert "anomaly_score" in pred
    assert "health_score" in pred
    assert "shap_factors" in pred
    assert isinstance(pred["shap_factors"], list)


def test_get_alerts():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)
    assert len(alerts) >= 1


def test_get_maintenance():
    response = client.get("/api/maintenance")
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)
    assert len(records) >= 1


def test_get_analytics():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    analytics = response.json()
    assert "kpis" in analytics
    assert analytics["kpis"]["total_machines"] >= 6
    assert "health_distribution" in analytics
    assert "model_benchmarks" in analytics


def test_ai_assistant_chat():
    payload = {
        "machine_id": "ENG-003",
        "query": "Why is ENG-003 showing a critical failure risk and what should we do?"
    }
    response = client.post("/api/assistant/chat", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert "ENG-003" in result["response"]
    assert "Diagnostic Report" in result["response"]
    assert "recommended_action" in result
