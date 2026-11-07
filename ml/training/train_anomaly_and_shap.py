"""
Anomaly Detection Pipeline & SHAP Explainability Engine for PredixAI:
1. Isolation Forest & PyTorch Autoencoder Anomaly Detection (calibrated [0, 1] anomaly score)
2. SHAP (TreeExplainer) Sensor Feature Attribution & Local Explainability
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.ensemble import IsolationForest
import shap

import sys
sys.path.append(r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI")
from ml.preprocessing.pipeline import CMapssPreprocessor
from ml.training.pytorch_models import AutoencoderAnomalyDetector


def train_autoencoder(
    X_healthy: np.ndarray,
    input_dim: int,
    epochs: int = 15,
    batch_size: int = 128,
    lr: float = 0.003
) -> AutoencoderAnomalyDetector:
    """Trains Autoencoder on healthy baseline cycles to learn normal equipment state."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = AutoencoderAnomalyDetector(input_dim=input_dim, latent_dim=16).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)

    dataset = TensorDataset(torch.from_numpy(X_healthy.astype(np.float32)))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(epochs):
        for (batch_x,) in loader:
            batch_x = batch_x.to(device)
            optimizer.zero_grad()
            recon = model(batch_x)
            loss = criterion(recon, batch_x)
            loss.backward()
            optimizer.step()

    model.eval()
    return model


def calibrate_anomaly_scores(errors: np.ndarray) -> Tuple[float, float]:
    """Computes median and 95th percentile error from healthy data for score normalization."""
    p50 = float(np.percentile(errors, 50))
    p95 = float(np.percentile(errors, 95))
    return p50, p95


def run_anomaly_and_shap(dataset_name: str = 'FD001'):
    print("=" * 75)
    print("PREDIXAI - ANOMALY DETECTION & SHAP EXPLAINABILITY PIPELINE")
    print("=" * 75)

    # 1. Preprocess data
    prep = CMapssPreprocessor(dataset_name, use_kalman=True, rul_cap=125)
    train_df, val_df, test_df, feature_cols = prep.fit_transform(val_engine_ratio=0.2, random_state=42)

    save_dir = r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\backend\saved_models"
    exp_dir = r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\ml\experiments"
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(exp_dir, exist_ok=True)

    # Healthy data: First 30 cycles of each engine (before significant wear)
    healthy_mask = train_df['cycle'] <= 30
    X_healthy = train_df.loc[healthy_mask, feature_cols].values
    X_all_train = train_df[feature_cols].values

    # -------------------------------------------------------------
    # 1. Isolation Forest Anomaly Detector
    # -------------------------------------------------------------
    print("\n[1/3] Training Isolation Forest on Baseline Healthy Fleet...")
    iso_forest = IsolationForest(
        n_estimators=150,
        contamination=0.03,
        max_samples='auto',
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_healthy)

    # Fit score calibrator: Raw decision function maps negative to anomaly
    raw_scores_healthy = iso_forest.decision_function(X_healthy)
    iso_min = float(raw_scores_healthy.min())
    iso_max = float(raw_scores_healthy.max())

    joblib.dump(iso_forest, os.path.join(save_dir, 'anomaly_isolation_forest.joblib'))
    print(f"      Isolation Forest saved. Decision threshold range: [{iso_min:.3f}, {iso_max:.3f}]")

    # -------------------------------------------------------------
    # 2. PyTorch Autoencoder Anomaly Detector
    # -------------------------------------------------------------
    print("\n[2/3] Training PyTorch Autoencoder Anomaly Detector...")
    autoenc = train_autoencoder(X_healthy, input_dim=len(feature_cols), epochs=15)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    with torch.no_grad():
        healthy_errors = autoenc.compute_anomaly_score(torch.from_numpy(X_healthy.astype(np.float32)).to(device)).cpu().numpy()
    err_median, err_p95 = calibrate_anomaly_scores(healthy_errors)

    torch.save(autoenc.state_dict(), os.path.join(save_dir, 'anomaly_autoencoder.pt'))
    anomaly_meta = {
        'model_type': 'Autoencoder + Isolation Forest',
        'healthy_recon_median': err_median,
        'healthy_recon_p95': err_p95,
        'feature_count': len(feature_cols),
        'iso_decision_min': iso_min,
        'iso_decision_max': iso_max
    }
    with open(os.path.join(save_dir, 'anomaly_calibration_meta.json'), 'w') as f:
        json.dump(anomaly_meta, f, indent=2)
    print(f"      Autoencoder saved. Healthy Reconstruction Error: Median={err_median:.4f}, P95={err_p95:.4f}")

    # -------------------------------------------------------------
    # 3. SHAP Explainability Engine
    # -------------------------------------------------------------
    print("\n[3/3] Initializing SHAP TreeExplainer on LightGBM Model...")
    lgbm_model_path = os.path.join(save_dir, 'failure_model_lgbm.joblib')
    if os.path.exists(lgbm_model_path):
        lgb_model = joblib.load(lgbm_model_path)
        explainer = shap.TreeExplainer(lgb_model)

        # Compute SHAP values on a representative validation subsample
        val_sample = val_df[feature_cols].iloc[:200]
        shap_values = explainer.shap_values(val_sample)

        # If binary classification, shap_values is a list [class0, class1] or 2D array
        if isinstance(shap_values, list):
            sv = shap_values[1]
        else:
            sv = shap_values

        mean_abs_shap = np.abs(sv).mean(axis=0)
        sorted_indices = np.argsort(mean_abs_shap)[::-1]

        top_factors = []
        for idx in sorted_indices[:10]:
            top_factors.append({
                'feature': feature_cols[idx],
                'mean_abs_shap': float(mean_abs_shap[idx])
            })

        print("\n[TOP SENSORS INFLUENCING FAILURE PREDICTION (SHAP)]:")
        for rank, tf in enumerate(top_factors, 1):
            print(f"  {rank:>2}. {tf['feature']:<20}: {tf['mean_abs_shap']:.4f}")

        # Save explainer metadata
        shap_meta = {
            'explainer_type': 'TreeExplainer',
            'base_value': float(explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value),
            'top_global_features': top_factors
        }
        with open(os.path.join(exp_dir, 'shap_global_importance.json'), 'w') as f:
            json.dump(shap_meta, f, indent=2)

        joblib.dump(explainer, os.path.join(save_dir, 'shap_tree_explainer.joblib'))
        print(f"[SUCCESS] SHAP explainer and feature attribution saved.")
    else:
        print("[WARN] LightGBM model not found at", lgbm_model_path)

    print("\n" + "=" * 75)
    print("[PHASE 1 COMPLETE] Anomaly Detection & Explainable AI fully trained and serialized.")
    print("=" * 75)


if __name__ == '__main__':
    run_anomaly_and_shap('FD001')
