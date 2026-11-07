# PredixAI System Architecture & Engineering Specifications

PredixAI is an enterprise-grade Industrial AI & Machine Health Monitoring Platform designed for continuous prognostics, Remaining Useful Life (RUL) estimation, and predictive maintenance.

---

## 1. High-Level System Architecture

```text
       [ NASA C-MAPSS / Physical Equipment ]
                       |
                       v
         [ Industrial IoT MQTT Broker ]
                       |
                       v
        [ FastAPI Prognostics Gateway ]
        +-----------------------------+
        | - Kalman Noise Filtering    |
        | - Operating Regime Cluster  |
        | - Feature Engineering Engine|
        +--------------+--------------+
                       |
         +-------------+-------------+
         |                           |
         v                           v
  [ Machine Learning Engine ]  [ Persistence Layer ]
  - Failure Clf (LightGBM/SVM) - PostgreSQL / SQLite
  - RUL Regressor (XGBoost)    - Time-series Telemetry
  - Anomaly Det (Autoencoder)  - Maintenance Orders
  - Explainable AI (SHAP)      - Automated Alerts
         |                           |
         +-------------+-------------+
                       |
                       v
       [ Real-time WebSocket Stream ]
                       |
                       v
     [ React + TypeScript Industrial UI ]
     +----------------------------------+
     | - Fleet Health Dashboard         |
     | - Machine Telemetry & Gauges     |
     | - 3D Digital Twin (Three.js)     |
     | - AI Maintenance Assistant (RAG) |
     | - Benchmarks & Analytics         |
     +----------------------------------+
```

---

## 2. Subsystem Breakdown

### A. Machine Learning Pipeline (`ml/`)
- **Noise Reduction**: Preserves and modernizes the hackathon's core insight with 1D Kalman state-space estimation per sensor channel ($R=0.15, Q=10^{-4}$).
- **Regime Normalization**: Employs K-Means ($k=6$) clustering across operational settings for multi-condition datasets (FD002/FD004) to normalize multi-altitude flight envelopes.
- **Engine-Level Group Splitting**: Prevents temporal and machine data leakage by strictly partitioning train and validation sets by `unit_id`.
- **Piecewise Linear RUL Target**: Evaluates capping at 125 operating cycles, drastically stabilizing early-cycle regression penalties.
- **Explainable AI (SHAP)**: Fast TreeExplainer computes real-time Shapley values attributing failure probability to physical sensor degradation.

### B. Backend REST & WebSocket Services (`backend/`)
- **FastAPI Framework**: Asynchronous endpoints for sub-millisecond telemetry ingestion and predictions.
- **SQLAlchemy ORM**: Flexible database connector supporting PostgreSQL and SQLite.
- **Rule Engine**: Computes composite health scores ($0-100\%$) and generates prescriptive industrial alerts.
- **AI Diagnostics Assistant**: RAG-grounded diagnostic agent that synthesizes machine telemetry, SHAP attributions, and maintenance manuals.

### C. Industrial Dashboard (`frontend/`)
- **React 18 + TypeScript**: Type-safe, componentized architecture.
- **Tailwind CSS**: Industrial dark mode aesthetic optimized for control room visibility.
- **Recharts**: Responsive real-time time-series degradation charts.
- **Three.js Digital Twin**: 3D geometric turbofan model with spinning wide-chord fan blades, compressor disks, and thermal wear heatmaps.
