# PredixAI Machine Learning & Prognostics Benchmark Documentation

## 1. Problem Formulation

Turbofan jet engine components (notably the High Pressure Compressor, HPC, and Low Pressure Turbine, LPT) undergo progressive structural, aerodynamic, and thermal degradation.
The prognostics objective is twofold:
1. **Failure Classification**: Predict whether catastrophic degradation will occur within a lookahead window $w_1 = 30$ cycles.
2. **Remaining Useful Life (RUL) Regression**: Predict the exact remaining operating cycles $RUL(t)$ until engine failure.

---

## 2. Dataset Profiling (NASA C-MAPSS FD001 - FD004)

| Dataset | Operating Conditions | Fault Modes | Train Engines | Test Engines | Constant Sensors Dropped |
|---|---|---|---|---|---|
| **FD001** | Sea Level (Single) | HPC Degradation | 100 | 100 | s1, s5, s10, s16, s18, s19 |
| **FD002** | 6 Flight Conditions | HPC Degradation | 260 | 259 | None (All 21 vary with flight regime) |
| **FD003** | Sea Level (Single) | HPC + Fan Degradation | 100 | 100 | s1, s5, s16, s18, s19 |
| **FD004** | 6 Flight Conditions | HPC + Fan Degradation | 249 | 248 | None (All 21 vary with flight regime) |

---

## 3. Evaluation Metrics

### NASA Asymmetric Scoring Function
Late predictions (predicting failure *after* it occurs) risk catastrophic industrial failure and are penalized exponentially higher than early predictions:
$$d_i = \hat{RUL}_i - RUL_i$$
$$s_i = \begin{cases} e^{-d_i / 13} - 1, & \text{if } d_i < 0 \text{ (Late Prediction)} \\ e^{d_i / 10} - 1, & \text{if } d_i \ge 0 \text{ (Early Prediction)} \end{cases}$$
$$S = \sum_{i=1}^N s_i$$

### False Negative Rate (FNR)
In industrial maintenance, missing an actual failing engine ($FN$) is vastly more expensive than a false alarm ($FP$):
$$FNR = \frac{FN}{TP + FN}$$

---

## 4. Benchmark Results (Official Test Set, 100 Engines)

### A. Failure Classification (Failure within 30 Cycles)

| Model Architecture | Accuracy | Precision | Recall | F1-Score | False Negative Rate (Low=Best) |
|---|---|---|---|---|---|
| **Support Vector Machine (RBF)** 🏆 | **96.0%** | 88.89% | **96.00%** | **0.9231** | **4.0%** |
| **LightGBM Classifier** | **96.0%** | **92.00%** | 92.00% | 0.9200 | 8.0% |
| **XGBoost Classifier** | 95.0% | 91.67% | 88.00% | 0.8980 | 12.0% |
| **PyTorch LSTM Classifier** | 95.0% | 91.67% | 88.00% | 0.8980 | 12.0% |
| **Random Forest (Baseline)** | 93.0% | 90.91% | 80.00% | 0.8511 | 20.0% |

### B. Remaining Useful Life (RUL) Regression

| Model Architecture | MAE (Cycles) | RMSE (Cycles) | $R^2$ Score | NASA Score | Late Pred % |
|---|---|---|---|---|---|
| **XGBoost Regressor (Capped 125)** 🏆 | **10.74** | **14.42** | **0.8796** | **300.2** | 49.0% |
| **LightGBM Regressor** | 11.29 | 14.96 | 0.8705 | 325.4 | 50.0% |
| **Random Forest Regressor** | 11.48 | 15.25 | 0.8653 | 386.2 | 43.0% |
| **PyTorch Kalman-LSTM** | 11.95 | 16.32 | 0.8458 | 382.9 | 60.0% |
| **XGBoost (Uncapped RUL)** | 18.61 | 26.03 | 0.6076 | 6669.4 | 36.0% |

> **Key Research Finding**: Piecewise linear capping ($RUL=125$) stabilized regression variance on healthy early cycles, reducing the exponential NASA penalty from 6,669.4 to 300.2 (a 95.5% improvement).

---

## 5. SHAP Feature Attribution Ranking

Global Shapley value analysis reveals the dominant sensor indicators driving failure risk:
1. `s11_lag_diff_3`: Rate of change in High Pressure Compressor Static Pressure (Ps30).
2. `s12_lag_diff_3`: Fuel flow ratio acceleration compensating for stage leakage.
3. `s3`: HPC Outlet Temperature (T30) thermal creep.
4. `s4`: Low Pressure Turbine (LPT) exhaust gas temperature divergence.
5. `s17`: Bleed Enthalpy (htBleed) interstage seal degradation.
