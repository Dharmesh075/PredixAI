"""
Benchmark and Modernize Failure Prediction Models (FD001):
1. Random Forest Classifier
2. XGBoost Classifier
3. LightGBM Classifier
4. Support Vector Machine (SVM)
5. PyTorch LSTM Classifier

Evaluates models with Engine-Level Splitting (preventing data leakage),
calculates standard metrics, and emphasizes the industrial False Negative Rate (FNR).
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from typing import Dict, Any, List

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import xgboost as xgb
import lightgbm as lgb

import sys
sys.path.append(r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI")
from ml.preprocessing.pipeline import CMapssPreprocessor, generate_sequences
from ml.training.pytorch_models import LSTMClassifier
from ml.evaluation.metrics import evaluate_classification


def train_lstm_classifier(
    X_train_seq: np.ndarray,
    y_train_seq: np.ndarray,
    X_val_seq: np.ndarray,
    y_val_seq: np.ndarray,
    input_dim: int,
    epochs: int = 15,
    batch_size: int = 128,
    lr: float = 0.002
) -> LSTMClassifier:
    """Trains PyTorch LSTM Classifier using BCEWithLogitsLoss."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = LSTMClassifier(input_dim=input_dim, hidden_dim=64, num_layers=2, dropout=0.2).to(device)

    # Class imbalance handling
    pos_weight = float((len(y_train_seq) - sum(y_train_seq)) / max(1, sum(y_train_seq)))
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]).to(device))
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    train_ds = TensorDataset(torch.from_numpy(X_train_seq), torch.from_numpy(y_train_seq))
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

    model.eval()
    return model


def evaluate_lstm(
    model: LSTMClassifier,
    X_seq: np.ndarray,
    threshold: float = 0.5
) -> Tuple[np.ndarray, np.ndarray]:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.eval()
    with torch.no_grad():
        x_tensor = torch.from_numpy(X_seq).to(device)
        logits = model(x_tensor)
        probs = torch.sigmoid(logits).cpu().numpy()
        preds = (probs >= threshold).astype(int)
    return preds, probs


def run_classification_benchmarks(dataset_name: str = 'FD001'):
    print("=" * 75)
    print(f"PREDIXAI - FAILURE PREDICTION BENCHMARKS ({dataset_name})")
    print("=" * 75)

    # 1. Preprocess data
    prep = CMapssPreprocessor(dataset_name, use_kalman=True, rul_cap=125, early_failure_window=30)
    train_df, val_df, test_df, feature_cols = prep.fit_transform(val_engine_ratio=0.2, random_state=42)

    X_train = train_df[feature_cols].values
    y_train = train_df['label_binary'].values

    X_val = val_df[feature_cols].values
    y_val = val_df['label_binary'].values

    # Test full and Test last-cycle (official evaluation)
    X_test_full = test_df[feature_cols].values
    y_test_full = test_df['label_binary'].values

    # Extract last cycle per test engine
    test_last_idx = test_df.groupby('unit_id')['cycle'].idxmax()
    X_test_last = test_df.loc[test_last_idx, feature_cols].values
    y_test_last = test_df.loc[test_last_idx, 'label_binary'].values

    print(f"[DATA] Train samples: {len(X_train)} | Val samples: {len(X_val)} | Test Last Engines: {len(X_test_last)}")
    print(f"[DATA] Features: {len(feature_cols)} | Positive class in Train: {y_train.mean():.1%}")

    benchmarks = {}
    trained_models = {}

    # -------------------------------------------------------------
    # Model 1: Random Forest Classifier (Baseline)
    # -------------------------------------------------------------
    print("\n[1/5] Training Random Forest Classifier...")
    rf = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1, class_weight='balanced')
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test_last)
    rf_probs = rf.predict_proba(X_test_last)[:, 1]
    rf_metrics = evaluate_classification(y_test_last, rf_preds, rf_probs)
    benchmarks['Random Forest'] = rf_metrics
    trained_models['Random Forest'] = rf
    print(f"      Accuracy: {rf_metrics['accuracy']:.4f} | Recall: {rf_metrics['recall']:.4f} | F1: {rf_metrics['f1_score']:.4f} | FNR: {rf_metrics['false_negative_rate']:.4f}")

    # -------------------------------------------------------------
    # Model 2: XGBoost Classifier
    # -------------------------------------------------------------
    print("\n[2/5] Training XGBoost Classifier...")
    scale_pos = (len(y_train) - sum(y_train)) / max(1, sum(y_train))
    xgb_clf = xgb.XGBClassifier(
        n_estimators=180,
        max_depth=5,
        learning_rate=0.04,
        subsample=0.8,
        colsample_bytree=0.7,
        scale_pos_weight=scale_pos,
        random_state=42,
        eval_metric='logloss'
    )
    xgb_clf.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    xgb_preds = xgb_clf.predict(X_test_last)
    xgb_probs = xgb_clf.predict_proba(X_test_last)[:, 1]
    xgb_metrics = evaluate_classification(y_test_last, xgb_preds, xgb_probs)
    benchmarks['XGBoost'] = xgb_metrics
    trained_models['XGBoost'] = xgb_clf
    print(f"      Accuracy: {xgb_metrics['accuracy']:.4f} | Recall: {xgb_metrics['recall']:.4f} | F1: {xgb_metrics['f1_score']:.4f} | FNR: {xgb_metrics['false_negative_rate']:.4f}")

    # -------------------------------------------------------------
    # Model 3: LightGBM Classifier
    # -------------------------------------------------------------
    print("\n[3/5] Training LightGBM Classifier...")
    lgb_clf = lgb.LGBMClassifier(
        n_estimators=160,
        max_depth=6,
        learning_rate=0.04,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.7,
        scale_pos_weight=scale_pos,
        random_state=42,
        verbosity=-1
    )
    lgb_clf.fit(X_train, y_train, eval_set=[(X_val, y_val)], callbacks=[])
    lgb_preds = lgb_clf.predict(X_test_last)
    lgb_probs = lgb_clf.predict_proba(X_test_last)[:, 1]
    lgb_metrics = evaluate_classification(y_test_last, lgb_preds, lgb_probs)
    benchmarks['LightGBM'] = lgb_metrics
    trained_models['LightGBM'] = lgb_clf
    print(f"      Accuracy: {lgb_metrics['accuracy']:.4f} | Recall: {lgb_metrics['recall']:.4f} | F1: {lgb_metrics['f1_score']:.4f} | FNR: {lgb_metrics['false_negative_rate']:.4f}")

    # -------------------------------------------------------------
    # Model 4: Support Vector Machine (SVM)
    # -------------------------------------------------------------
    print("\n[4/5] Training Support Vector Machine (SVM RBF)...")
    svm_clf = SVC(kernel='rbf', C=1.5, probability=True, class_weight='balanced', random_state=42)
    # Train on subsample to keep execution snappy while accurate
    sub_idx = np.random.choice(len(X_train), size=min(8000, len(X_train)), replace=False)
    svm_clf.fit(X_train[sub_idx], y_train[sub_idx])
    svm_preds = svm_clf.predict(X_test_last)
    svm_probs = svm_clf.predict_proba(X_test_last)[:, 1]
    svm_metrics = evaluate_classification(y_test_last, svm_preds, svm_probs)
    benchmarks['SVM'] = svm_metrics
    trained_models['SVM'] = svm_clf
    print(f"      Accuracy: {svm_metrics['accuracy']:.4f} | Recall: {svm_metrics['recall']:.4f} | F1: {svm_metrics['f1_score']:.4f} | FNR: {svm_metrics['false_negative_rate']:.4f}")

    # -------------------------------------------------------------
    # Model 5: PyTorch LSTM Classifier (Sequential)
    # -------------------------------------------------------------
    print("\n[5/5] Training PyTorch LSTM Classifier...")
    seq_len = 30
    X_train_seq, y_train_seq, _ = generate_sequences(train_df, feature_cols, seq_length=seq_len, target_col='label_binary')
    X_val_seq, y_val_seq, _ = generate_sequences(val_df, feature_cols, seq_length=seq_len, target_col='label_binary')
    X_test_last_seq, y_test_last_seq, _ = generate_sequences(test_df, feature_cols, seq_length=seq_len, target_col='label_binary', last_only=True)

    lstm_clf = train_lstm_classifier(
        X_train_seq, y_train_seq,
        X_val_seq, y_val_seq,
        input_dim=len(feature_cols),
        epochs=12,
        batch_size=128,
        lr=0.002
    )
    lstm_preds, lstm_probs = evaluate_lstm(lstm_clf, X_test_last_seq, threshold=0.5)
    lstm_metrics = evaluate_classification(y_test_last_seq, lstm_preds, lstm_probs)
    benchmarks['LSTM'] = lstm_metrics
    print(f"      Accuracy: {lstm_metrics['accuracy']:.4f} | Recall: {lstm_metrics['recall']:.4f} | F1: {lstm_metrics['f1_score']:.4f} | FNR: {lstm_metrics['false_negative_rate']:.4f}")

    # -------------------------------------------------------------
    # Summary Table & Champion Selection
    # -------------------------------------------------------------
    print("\n" + "=" * 75)
    print(f"{'MODEL':<18} | {'ACCURACY':<9} | {'PRECISION':<9} | {'RECALL':<8} | {'F1-SCORE':<8} | {'FNR (Low=Best)':<14}")
    print("-" * 75)
    for model_name, m in benchmarks.items():
        print(f"{model_name:<18} | {m['accuracy']:<9.4f} | {m['precision']:<9.4f} | {m['recall']:<8.4f} | {m['f1_score']:<8.4f} | {m['false_negative_rate']:<14.4f}")
    print("=" * 75)

    # Select champion (highest F1 and lowest FNR)
    champion_name = max(benchmarks.keys(), key=lambda k: (benchmarks[k]['f1_score'], -benchmarks[k]['false_negative_rate']))
    print(f"\n[CHAMPION] Top Failure Classification Model: {champion_name} (F1: {benchmarks[champion_name]['f1_score']:.4f})")

    # Save artifacts
    save_dir = r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\backend\saved_models"
    exp_dir = r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\ml\experiments"
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(exp_dir, exist_ok=True)

    # Save champion model
    if champion_name == 'LSTM':
        torch.save(lstm_clf.state_dict(), os.path.join(save_dir, 'failure_model_lstm.pt'))
    else:
        joblib.dump(trained_models[champion_name], os.path.join(save_dir, 'failure_model_champion.joblib'))

    # Also save LightGBM and XGBoost for fast API inference & SHAP explainability
    joblib.dump(trained_models['LightGBM'], os.path.join(save_dir, 'failure_model_lgbm.joblib'))
    joblib.dump(trained_models['XGBoost'], os.path.join(save_dir, 'failure_model_xgboost.joblib'))

    # Save preprocessor artifacts
    prep.save_artifacts(save_dir)

    # Save benchmark json
    with open(os.path.join(exp_dir, f'{dataset_name}_classification_benchmarks.json'), 'w') as f:
        json.dump(benchmarks, f, indent=2)

    print(f"[SUCCESS] Models and benchmark metrics saved to {save_dir} and {exp_dir}")
    return benchmarks


if __name__ == '__main__':
    run_classification_benchmarks('FD001')
