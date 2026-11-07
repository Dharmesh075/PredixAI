# PredixAI
### Intelligent Predictive Maintenance & Machine Health Monitoring Platform
*Modernized from the award-winning Siemens MakeIT Real Hackathon research into a full-scale industrial prognostics platform.*

---

## 🌟 Executive Summary

**PredixAI** is an AI-powered industrial intelligence platform that monitors machinery, predicts imminent failures, estimates **Remaining Useful Life (RUL)**, detects multivariate sensor anomalies, and prescribes automated maintenance schedules.

Rooted in NASA's turbofan degradation simulation datasets (C-MAPSS FD001 to FD004), PredixAI modernizes the original Kalman Filter + LSTM approach into a production-grade system featuring:
- **Zero-Leakage ML Engineering**: Engine-level group partitioning preventing data leakage across train and validation splits.
- **Industrial-Grade Benchmarking**: Optimizing for **False Negative Rate (FNR)** and the asymmetric **NASA Scoring Function** (penalizing late predictions exponentially).
- **Explainable AI (SHAP)**: Fast TreeExplainer providing root-cause sensor attributions so maintenance engineers know *why* a machine is at risk.
- **Interactive 3D Digital Twin**: Real-time Three.js aerothermal model visualizing fan rotation, thermal wear heatmaps, and structural status.
- **RAG-Grounded AI Diagnostics Assistant**: Synthesizes live telemetry, SHAP factors, and equipment technical manuals to prescribe Standard Operating Procedures (SOPs).
- **Industrial IoT Simulator**: Real-time MQTT and REST telemetry streaming playing back authentic run-to-failure cycles.

---

## 🏗️ Architecture

```text
       [ Physical Sensors / NASA C-MAPSS Telemetry ]
                           |
                           v
              [ MQTT Broker / REST Ingest ]
                           |
                           v
           +-------------------------------+
           |    FastAPI Prognostics Engine  |
           | - 1D Kalman Noise Filtering   |
           | - Flight Regime Clustering    |
           | - Rolling Feature Extraction  |
           +---------------+---------------+
                           |
            +--------------+--------------+
            |                             |
            v                             v
  [ AI Prognostics Models ]      [ Database Layer ]
  - SVM / LightGBM (Clf)         - PostgreSQL / SQLite
  - XGBoost (RUL Regressor)      - Sensor Time-Series
  - Isolation Forest / Autoenc   - Work Orders & Alerts
  - SHAP TreeExplainer           - Model Version Registry
            |                             |
            +--------------+--------------+
                           |
                           v
              [ WebSocket Telemetry Stream ]
                           |
                           v
         [ React 18 + TypeScript Dashboard ]
         - Fleet Health Status & KPIs
         - Real-time Multi-sensor Telemetry
         - 3D Digital Twin (Three.js)
         - Explainable AI (SHAP) Waterfall
         - Automated Work Order Dispatcher
```

---

## 📊 Model Benchmarks (Official NASA Test Set, 100 Engines)

### 1. Failure Prediction Benchmark (Failure within 30 Cycles)

| Model Architecture | Accuracy | Precision | Recall | F1-Score | False Negative Rate (FNR) |
|---|---|---|---|---|---|
| **Support Vector Machine (RBF)** 🏆 | **96.0%** | 88.89% | **96.00%** | **0.9231** | **4.0%** |
| **LightGBM Classifier** | **96.0%** | **92.00%** | 92.00% | 0.9200 | 8.0% |
| **XGBoost Classifier** | 95.0% | 91.67% | 88.00% | 0.8980 | 12.0% |
| **PyTorch LSTM Classifier** | 95.0% | 91.67% | 88.00% | 0.8980 | 12.0% |
| **Random Forest (Baseline)** | 93.0% | 90.91% | 80.00% | 0.8511 | 20.0% |

### 2. Remaining Useful Life (RUL) Regression

| Model Architecture | MAE (Cycles) | RMSE (Cycles) | $R^2$ Score | NASA Score (Low=Best) | Late Pred % |
|---|---|---|---|---|---|
| **XGBoost Regressor (Capped 125)** 🏆 | **10.74** | **14.42** | **0.8796** | **300.2** | 49.0% |
| **LightGBM Regressor** | 11.29 | 14.96 | 0.8705 | 325.4 | 50.0% |
| **Random Forest Regressor** | 11.48 | 15.25 | 0.8653 | 386.2 | 43.0% |
| **PyTorch Kalman-LSTM** | 11.95 | 16.32 | 0.8458 | 382.9 | 60.0% |
| **XGBoost (Uncapped RUL)** | 18.61 | 26.03 | 0.6076 | 6669.4 | 36.0% |

> **Research Finding:** Piecewise linear capping ($RUL = 125$) reduced the exponential NASA penalty by **95.5%** (from 6,669.4 to 300.2) by bounding early-cycle overestimation.

---

## 📁 Repository Structure

```text
PredixAI/
│
├── frontend/                     # React + TypeScript + Tailwind + Recharts + Three.js
│   ├── src/
│   │   ├── components/           # Sidebar, Header, DigitalTwin (3D), AssistantDrawer
│   │   ├── pages/                # Overview, Monitoring, Predictions, Alerts, Maintenance, Analytics
│   │   ├── services/api.ts       # REST & WebSocket API client
│   │   └── types/index.ts        # Industrial telemetry TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                      # High-Performance FastAPI Backend
│   ├── app/
│   │   ├── main.py               # Application entrypoint & WebSockets
│   │   ├── api/                  # REST routers (machines, predict, alerts, maintenance, assistant)
│   │   ├── database/             # SQLAlchemy ORM models & connection
│   │   ├── models/               # Pydantic schemas
│   │   └── services/             # Prediction service, Alert service, Health score engine
│   ├── saved_models/             # Champion model weights, scalers & metadata
│   ├── tests/                    # API integration tests
│   └── requirements.txt
│
├── ml/                           # Machine Learning & Prognostics Pipeline
│   ├── datasets/                 # NASA C-MAPSS subsets (FD001 to FD004)
│   ├── notebooks/original/       # Historical Siemens Hackathon research (preserved!)
│   ├── preprocessing/            # Reusable preprocessor, Kalman filter, EDA profiler
│   ├── training/                 # Benchmarking scripts (classification, regression, anomaly & SHAP)
│   ├── evaluation/               # NASA scoring function & metrics
│   └── experiments/              # Benchmark JSON records & SHAP global importance
│
├── simulator/                    # Industrial IoT Telemetry Simulators
│   ├── sensor_simulator.py       # REST telemetry playback from test engines
│   └── mqtt_publisher.py         # MQTT publisher for Mosquitto
│
├── docs/                         # Technical Documentation
│   ├── architecture.md           # System design & architecture
│   ├── model_documentation.md    # Mathematical equations & benchmark results
│   ├── api.md                    # REST & WebSocket specifications
│   └── ORIGINAL_README.md        # Original Hackathon documentation
│
├── docker/                       # Containerization
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docker-compose.yml            # Multi-container orchestration (Postgres, Mosquitto, Backend, Frontend)
└── README.md
```

---

## 🚀 Quickstart Guide

### Option A: Local Development (Fastest)

#### 1. Start the Backend API
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
*API is accessible at `http://localhost:8000`. Interactive documentation at `http://localhost:8000/docs`.*

#### 2. Start the React Industrial Dashboard
```bash
cd frontend
npm run dev
```
*Open `http://localhost:5173` in your browser.*

#### 3. Run the Live Telemetry Simulator (Optional)
```bash
python simulator/sensor_simulator.py --engine 1 --interval 0.5 --cycles 30
```
*Streams 30 run-to-failure cycles from NASA engine ENG-001 into the backend.*

---

### Option B: Docker Compose

```bash
docker-compose up --build
```
This spins up:
- **Frontend Dashboard**: `http://localhost:3000`
- **FastAPI API**: `http://localhost:8000`
- **PostgreSQL Database**: `localhost:5432`
- **Mosquitto MQTT Broker**: `localhost:1883`

---

## 🛠️ Verification & Testing

To run the automated backend test suite:
```bash
python backend/tests/run_tests.py
```

To re-run the ML benchmarks:
```bash
python ml/training/train_classification.py
python ml/training/train_regression.py
python ml/training/train_anomaly_and_shap.py
```

---

## 📄 License & Attribution
Modernized and expanded from the Siemens MakeIT Real Hackathon 4th-prize winning solution (original research preserved in `ml/notebooks/original/`). Datasets provided by the NASA Ames Prognostics Center of Excellence (PCoE).
