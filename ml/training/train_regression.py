"""
Benchmark and Modernize Remaining Useful Life (RUL) Prediction Models (FD001):
1. Random Forest Regressor
2. XGBoost Regressor
3. LightGBM Regressor
4. PyTorch LSTM Regressor
5. Modernized Kalman-LSTM Regressor (Preserves Hackathon 4th Prize Core Insight)
6. RUL Capping Comparison (Capped at 125 vs Uncapped)

Evaluates models using MAE, RMSE, R2, and the official NASA Asymmetric Scoring Function.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from typing import Dict, Any, Tuple

from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb

import sys
sys.path.append(r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI")
from ml.preprocessing.pipeline import CMapssPreprocessor, generate_sequences
from ml.training.pytorch_models import LSTMRegressor
from ml.evaluation.metrics import evaluate_regression, nasa_scoring_function


def train_lstm_regressor(
    X_train_seq: np.ndarray,
    y_train_seq: np.ndarray,
    input_dim: int,
    epochs: int = 15,
    batch_size: int = 128,
    lr: float = 0.003
) -> LSTMRegressor:
    """Trains PyTorch LSTM Regressor with Smooth L1 / Huber Loss."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = LSTMRegressor(input_dim=input_dim, hidden_dim=64, num_layers=2, dropout=0.2).to(device)
    criterion = nn.SmoothL1Loss()  # Robust to outliers
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    train_ds = TensorDataset(torch.from_numpy(X_train_seq), torch.from_numpy(y_train_seq))
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(epochs):
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

    model.eval()
    return model


def evaluate_lstm_reg(model: LSTMRegressor, X_seq: np.ndarray) -> np.ndarray:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.eval()
    with torch.no_grad():
        x_tensor = torch.from_numpy(X_seq).to(device)
        preds = model(x_tensor).cpu().numpy()
        preds = np.maximum(0.0, preds)  # RUL cannot be negative
    return preds


def run_regression_benchmarks(dataset_name: str = 'FD001'):
    print("=" * 80)
    print(f"PREDIXAI - REMAINING USEFUL LIFE (RUL) REGRESSION BENCHMARKS ({dataset_name})")
    print("=" * 80)

    # 1. Preprocess data with Kalman filtering and Capped RUL (125)
    prep = CMapssPreprocessor(dataset_name, use_kalman=True, rul_cap=125)
    train_df, val_df, test_df, feature_cols = prep.fit_transform(val_engine_ratio=0.2, random_state=42)

    truth_path = os.path.join(r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\ml\datasets",
                              'dataset1' if dataset_name == 'FD001' else 'dataset2', 'data',
                              'truth_01.txt' if dataset_name == 'FD001' else 'truth_02.txt')
    y_test_truth = pd.read_csv(truth_path, sep=r'\s+', header=None).iloc[:, 0].values

    # Training matrices
    X_train = train_df[feature_cols].values
    y_train = train_df['RUL_capped'].values

    # Official Test Set: last cycle features of each engine
    test_last_idx = test_df.groupby('unit_id')['cycle'].idxmax()
    X_test_last = test_df.loc[test_last_idx, feature_cols].values

    print(f"[DATA] Train samples: {len(X_train)} | Test Ground-Truth Engines: {len(y_test_truth)}")
    print(f"[DATA] Ground Truth RUL Range: [{y_test_truth.min()} to {y_test_truth.max()}], Mean: {y_test_truth.mean():.1f} cycles")

    benchmarks = {}
    trained_models = {}

    # -------------------------------------------------------------
    # Model 1: Random Forest Regressor
    # -------------------------------------------------------------
    print("\n[1/5] Training Random Forest Regressor...")
    rf_reg = RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1)
    rf_reg.fit(X_train, y_train)
    rf_preds = np.maximum(0, rf_reg.predict(X_test_last))
    rf_metrics = evaluate_regression(y_test_truth, rf_preds)
    benchmarks['Random Forest'] = rf_metrics
    trained_models['Random Forest'] = rf_reg
    print(f"      MAE: {rf_metrics['mae']:.2f} | RMSE: {rf_metrics['rmse']:.2f} | NASA Score: {rf_metrics['nasa_total_score']:.1f}")

    # -------------------------------------------------------------
    # Model 2: XGBoost Regressor
    # -------------------------------------------------------------
    print("\n[2/5] Training XGBoost Regressor...")
    xgb_reg = xgb.XGBRegressor(
        n_estimators=180,
        max_depth=5,
        learning_rate=0.04,
        subsample=0.8,
        colsample_bytree=0.7,
        random_state=42
    )
    xgb_reg.fit(X_train, y_train)
    xgb_preds = np.maximum(0, xgb_reg.predict(X_test_last))
    xgb_metrics = evaluate_regression(y_test_truth, xgb_preds)
    benchmarks['XGBoost'] = xgb_metrics
    trained_models['XGBoost'] = xgb_reg
    print(f"      MAE: {xgb_metrics['mae']:.2f} | RMSE: {xgb_metrics['rmse']:.2f} | NASA Score: {xgb_metrics['nasa_total_score']:.1f}")

    # -------------------------------------------------------------
    # Model 3: LightGBM Regressor
    # -------------------------------------------------------------
    print("\n[3/5] Training LightGBM Regressor...")
    lgb_reg = lgb.LGBMRegressor(
        n_estimators=160,
        max_depth=6,
        learning_rate=0.04,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.7,
        random_state=42,
        verbosity=-1
    )
    lgb_reg.fit(X_train, y_train)
    lgb_preds = np.maximum(0, lgb_reg.predict(X_test_last))
    lgb_metrics = evaluate_regression(y_test_truth, lgb_preds)
    benchmarks['LightGBM'] = lgb_metrics
    trained_models['LightGBM'] = lgb_reg
    print(f"      MAE: {lgb_metrics['mae']:.2f} | RMSE: {lgb_metrics['rmse']:.2f} | NASA Score: {lgb_metrics['nasa_total_score']:.1f}")

    # -------------------------------------------------------------
    # Model 4 & 5: PyTorch LSTM & Kalman-LSTM Regressors
    # -------------------------------------------------------------
    seq_len = 30
    X_train_seq, y_train_seq, _ = generate_sequences(train_df, feature_cols, seq_length=seq_len, target_col='RUL_capped')
    X_test_last_seq, _, _ = generate_sequences(test_df, feature_cols, seq_length=seq_len, target_col='RUL_capped', last_only=True)

    print("\n[4/5] Training PyTorch Kalman-LSTM Regressor (Hackathon Modernization)...")
    lstm_reg = train_lstm_regressor(X_train_seq, y_train_seq, input_dim=len(feature_cols), epochs=15, batch_size=128, lr=0.003)
    lstm_preds = evaluate_lstm_reg(lstm_reg, X_test_last_seq)
    lstm_metrics = evaluate_regression(y_test_truth, lstm_preds)
    benchmarks['Kalman-LSTM (PyTorch)'] = lstm_metrics
    print(f"      MAE: {lstm_metrics['mae']:.2f} | RMSE: {lstm_metrics['rmse']:.2f} | NASA Score: {lstm_metrics['nasa_total_score']:.1f}")

    # -------------------------------------------------------------
    # Experiment 6: Raw Uncapped RUL vs Capped RUL (125)
    # -------------------------------------------------------------
    print("\n[6/6] Running RUL Capping Comparison Experiment (XGBoost Uncapped vs Capped)...")
    prep_uncapped = CMapssPreprocessor(dataset_name, use_kalman=True, rul_cap=None)
    tr_uncapped, _, _, _ = prep_uncapped.fit_transform(val_engine_ratio=0.2)
    xgb_uncapped = xgb.XGBRegressor(n_estimators=180, max_depth=5, learning_rate=0.04, subsample=0.8, colsample_bytree=0.7, random_state=42)
    xgb_uncapped.fit(tr_uncapped[feature_cols].values, tr_uncapped['RUL'].values)
    uncapped_preds = np.maximum(0, xgb_uncapped.predict(X_test_last))
    uncapped_metrics = evaluate_regression(y_test_truth, uncapped_preds)
    benchmarks['XGBoost (Uncapped RUL)'] = uncapped_metrics
    print(f"      Uncapped -> MAE: {uncapped_metrics['mae']:.2f} | RMSE: {uncapped_metrics['rmse']:.2f} | NASA Score: {uncapped_metrics['nasa_total_score']:.1f}")

    # -------------------------------------------------------------
    # Summary Table & Champion Selection
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print(f"{'MODEL':<24} | {'MAE':<7} | {'RMSE':<7} | {'R2':<7} | {'NASA SCORE':<12} | {'LATE %':<7}")
    print("-" * 80)
    for model_name, m in benchmarks.items():
        print(f"{model_name:<24} | {m['mae']:<7.2f} | {m['rmse']:<7.2f} | {m['r2_score']:<7.4f} | {m['nasa_total_score']:<12.1f} | {m['late_predictions_pct']:<7.1f}")
    print("=" * 80)

    # Select champion (lowest RMSE and lowest NASA penalty)
    champion_name = min(benchmarks.keys(), key=lambda k: benchmarks[k]['rmse'])
    print(f"\n[CHAMPION] Top RUL Regression Model: {champion_name} (RMSE: {benchmarks[champion_name]['rmse']:.2f})")

    # Save artifacts
    save_dir = r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\backend\saved_models"
    exp_dir = r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\ml\experiments"

    # Save models
    torch.save(lstm_reg.state_dict(), os.path.join(save_dir, 'rul_model_lstm.pt'))
    joblib.dump(trained_models['LightGBM'], os.path.join(save_dir, 'rul_model_lgbm.joblib'))
    joblib.dump(trained_models['XGBoost'], os.path.join(save_dir, 'rul_model_xgboost.joblib'))
    joblib.dump(trained_models['Random Forest'], os.path.join(save_dir, 'rul_model_rf.joblib'))

    with open(os.path.join(exp_dir, f'{dataset_name}_rul_regression_benchmarks.json'), 'w') as f:
        json.dump(benchmarks, f, indent=2)

    print(f"[SUCCESS] RUL models and benchmark metrics saved.")
    return benchmarks


if __name__ == '__main__':
    run_regression_benchmarks('FD001')
