# PredixAI REST & WebSocket API Documentation

Base URL: `http://localhost:8000`
Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 1. Machine Management

### `GET /api/machines`
Returns list of all monitored industrial equipment.

### `POST /api/machines`
Registers a new industrial unit.
```json
{
  "machine_id": "ENG-007",
  "name": "GE Aviation GE9X #07",
  "machine_type": "Turbofan Engine",
  "model_series": "GE9X-105B1A",
  "location": "Facility Alpha - Bay 4"
}
```

### `GET /api/machines/{machine_id}`
Returns equipment telemetry status, past 50 cycle readings, active alerts, and SHAP factors.

---

## 2. Machine Learning Predictions

### `POST /api/predict/full`
Primary real-time telemetry ingestion endpoint. Executes Kalman filtering, failure prediction, RUL regression, anomaly detection, SHAP attribution, alert processing, and database persistence in a single call.
```json
{
  "machine_id": "ENG-001",
  "cycle": 125,
  "setting1": -0.0007,
  "setting2": -0.0004,
  "setting3": 100.0,
  "s2": 642.15,
  "s3": 1589.70,
  "s4": 1404.20,
  "s7": 553.80,
  "s8": 2388.06,
  "s9": 9046.19,
  "s11": 47.47,
  "s12": 521.66,
  "s13": 2388.02,
  "s14": 8138.62,
  "s15": 8.4195,
  "s17": 392.0,
  "s20": 39.06,
  "s21": 23.4190
}
```
**Response:**
```json
{
  "machine_id": "ENG-001",
  "cycle": 125,
  "failure_probability": 0.0002,
  "predicted_rul": 122.2,
  "anomaly_score": 0.038,
  "is_anomalous": false,
  "risk_level": "Normal",
  "health_score": 96.5,
  "confidence": 0.94,
  "shap_factors": [
    {
      "sensor": "s11_lag_diff_3",
      "sensor_name": "HPC Static Pressure (Ps30)",
      "contribution": 0.6307,
      "impact": "Increases Failure Risk",
      "description": "Rate of change in compressor static pressure indicates mechanical wear."
    }
  ]
}
```

---

## 3. Alerts & Maintenance

### `GET /api/alerts`
Query parameters: `machine_id`, `severity`, `is_acknowledged`.

### `PATCH /api/alerts/{id}/acknowledge`
Marks alert as acknowledged by plant operator.

### `GET /api/maintenance`
Returns all scheduled and completed work orders.

### `POST /api/maintenance`
Schedules a new maintenance action.

---

## 4. AI Diagnostics Assistant

### `POST /api/assistant/chat`
RAG-grounded diagnostic reasoning over machine history and SHAP factors.
```json
{
  "machine_id": "ENG-003",
  "query": "Why is ENG-003 showing a critical failure warning?"
}
```

---

## 5. WebSockets

### `WS /ws/telemetry`
Real-time duplex stream broadcasting live sensor telemetry and new predictions to connected industrial dashboard clients.
