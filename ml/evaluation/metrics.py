"""
Industrial Evaluation Metrics for Predictive Maintenance & Prognostics.
Includes Standard ML Metrics + Domain-Specific Metrics (NASA Scoring Function, FNR).
"""

import numpy as np
from typing import Dict, Any
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


def nasa_scoring_function(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes the official NASA C-MAPSS asymmetric evaluation metric:
    Penalty is heavily asymmetric: late predictions (predicting failure later than actual)
    are penalized exponentially more severely than early predictions.
    
    d_i = y_pred_i - y_true_i
    if d_i < 0: s_i = exp(-d_i / 13) - 1   (Late prediction)
    if d_i >= 0: s_i = exp(d_i / 10) - 1   (Early prediction)
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    d = y_pred - y_true

    late_mask = d < 0
    early_mask = d >= 0

    scores = np.zeros_like(d)
    scores[late_mask] = np.exp(-d[late_mask] / 13.0) - 1.0
    scores[early_mask] = np.exp(d[early_mask] / 10.0) - 1.0

    total_score = float(np.sum(scores))
    mean_score = float(np.mean(scores))
    late_pct = float(np.mean(late_mask) * 100.0)
    early_pct = float(np.mean(early_mask) * 100.0)

    return {
        'nasa_total_score': round(total_score, 2),
        'nasa_mean_penalty': round(mean_score, 4),
        'late_predictions_pct': round(late_pct, 1),
        'early_predictions_pct': round(early_pct, 1)
    }


def evaluate_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray = None
) -> Dict[str, Any]:
    """
    Evaluates binary failure classification with a focus on False Negative Rate.
    """
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn = fp = fn = tp = 0

    # False Negative Rate = FN / (FN + TP)
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    # False Positive Rate = FP / (FP + TN)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    metrics = {
        'accuracy': round(float(acc), 4),
        'precision': round(float(prec), 4),
        'recall': round(float(rec), 4),
        'f1_score': round(float(f1), 4),
        'false_negative_rate': round(float(fnr), 4),
        'false_positive_rate': round(float(fpr), 4),
        'confusion_matrix': {
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp)
        }
    }

    if y_prob is not None:
        try:
            metrics['roc_auc'] = round(float(roc_auc_score(y_true, y_prob)), 4)
            metrics['pr_auc'] = round(float(average_precision_score(y_true, y_prob)), 4)
        except Exception:
            metrics['roc_auc'] = None
            metrics['pr_auc'] = None

    return metrics


def evaluate_regression(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, Any]:
    """
    Evaluates RUL regression performance using MAE, RMSE, R2, and NASA asymmetric score.
    """
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    nasa_metrics = nasa_scoring_function(y_true, y_pred)

    result = {
        'mae': round(float(mae), 3),
        'rmse': round(float(rmse), 3),
        'r2_score': round(float(r2), 4),
        **nasa_metrics
    }
    return result
