"""
Reusable Preprocessing and Feature Engineering Pipeline for NASA C-MAPSS Datasets.
Supports FD001, FD002, FD003, and FD004 with dataset-specific regime handling,
Kalman filtering, engine-level group splitting, and sequence generation.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans

COLUMNS = ['unit_id', 'cycle', 'setting1', 'setting2', 'setting3'] + [f's{i}' for i in range(1, 22)]
SETTINGS = ['setting1', 'setting2', 'setting3']
ALL_SENSORS = [f's{i}' for i in range(1, 22)]

# Constant sensors identified per dataset
DATASET_CONSTANT_SENSORS = {
    'FD001': ['s1', 's5', 's10', 's16', 's18', 's19'],
    'FD002': [],
    'FD003': ['s1', 's5', 's16', 's18', 's19'],
    'FD004': []
}


class KalmanFilter1D:
    """
    1D Kalman Filter for smoothing noisy sensor time series.
    Vectorized and computationally efficient.
    """
    def __init__(self, r: float = 0.1, q: float = 1e-4):
        self.r = r  # Measurement noise covariance
        self.q = q  # Process noise covariance

    def filter(self, series: np.ndarray) -> np.ndarray:
        n = len(series)
        if n == 0:
            return series
        filtered = np.zeros(n)
        # Initialize
        x_est = series[0]
        p_est = 1.0

        for t in range(n):
            # Prediction step
            x_pred = x_est
            p_pred = p_est + self.q

            # Update step
            k_gain = p_pred / (p_pred + self.r)
            x_est = x_pred + k_gain * (series[t] - x_pred)
            p_est = (1.0 - k_gain) * p_pred
            filtered[t] = x_est

        return filtered


def apply_kalman_smoothing(df: pd.DataFrame, sensor_cols: List[str]) -> pd.DataFrame:
    """Applies 1D Kalman filter to sensor columns per engine unit."""
    df_smoothed = df.copy()
    kf = KalmanFilter1D(r=0.15, q=1e-4)

    for unit_id, group in df_smoothed.groupby('unit_id'):
        idx = group.index
        for col in sensor_cols:
            df_smoothed.loc[idx, col] = kf.filter(group[col].to_numpy(dtype=float))

    return df_smoothed


class CMapssPreprocessor:
    """
    Unified, state-of-the-art preprocessor for NASA C-MAPSS datasets.
    Handles single-condition (FD001, FD003) and multi-condition (FD002, FD004) datasets.
    """
    def __init__(
        self,
        dataset_name: str = 'FD001',
        data_dir: str = r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\ml\datasets",
        rul_cap: Optional[int] = 125,
        early_failure_window: int = 30,
        warning_window: int = 15,
        use_kalman: bool = True,
        rolling_window: int = 5,
        scale_type: str = 'standard'
    ):
        self.dataset_name = dataset_name
        self.data_dir = data_dir
        self.rul_cap = rul_cap
        self.w1 = early_failure_window
        self.w0 = warning_window
        self.use_kalman = use_kalman
        self.rolling_window = rolling_window
        self.scale_type = scale_type

        # Subset directory mapping
        subset_map = {
            'FD001': ('dataset1', '01'),
            'FD002': ('dataset2', '02'),
            'FD003': ('dataset3', '03'),
            'FD004': ('dataset4', '04')
        }
        folder, num = subset_map[dataset_name]
        self.train_path = os.path.join(data_dir, folder, 'data', f'train_{num}.txt')
        self.test_path = os.path.join(data_dir, folder, 'data', f'test_{num}.txt')
        self.truth_path = os.path.join(data_dir, folder, 'data', f'truth_{num}.txt')

        # Drop constant sensors
        self.constant_sensors = DATASET_CONSTANT_SENSORS.get(dataset_name, [])
        self.active_sensors = [s for s in ALL_SENSORS if s not in self.constant_sensors]

        self.scaler = StandardScaler() if scale_type == 'standard' else MinMaxScaler(feature_range=(-1, 1))
        self.feature_cols: List[str] = []
        self.is_fitted = False
        self.regime_kmeans: Optional[KMeans] = None

    def load_raw(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath, sep=r'\s+', header=None)
        df = df.iloc[:, :26]
        df.columns = COLUMNS
        # Ensure sensors and operational settings are float64 to avoid dtype mismatch in pandas 3.0
        float_cols = SETTINGS + ALL_SENSORS
        df[float_cols] = df[float_cols].astype(np.float64)
        df['unit_id'] = df['unit_id'].astype(np.int32)
        df['cycle'] = df['cycle'].astype(np.int32)
        df = df.sort_values(['unit_id', 'cycle']).reset_index(drop=True)
        return df

    def compute_regimes(self, df: pd.DataFrame, fit: bool = False) -> np.ndarray:
        """For multi-condition datasets (FD002, FD004), clusters operational settings into 6 regimes."""
        if self.dataset_name not in ['FD002', 'FD004']:
            return np.zeros(len(df), dtype=int)

        settings_data = df[SETTINGS].values
        if fit:
            self.regime_kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
            regimes = self.regime_kmeans.fit_predict(settings_data)
        else:
            if self.regime_kmeans is None:
                raise ValueError("Regime KMeans is not fitted.")
            regimes = self.regime_kmeans.predict(settings_data)
        return regimes

    def add_labels_train(self, train_df: pd.DataFrame) -> pd.DataFrame:
        """Generates RUL, capped RUL, binary label, and multiclass alert levels for training data."""
        df = train_df.copy()
        # Find maximum cycle per unit
        max_cycle = df.groupby('unit_id')['cycle'].max().reset_index()
        max_cycle.columns = ['unit_id', 'max_cycle']
        df = df.merge(max_cycle, on='unit_id', how='left')

        # True RUL: Remaining cycles until failure
        df['RUL'] = df['max_cycle'] - df['cycle']
        df.drop(columns=['max_cycle'], inplace=True)

        # Capped RUL (for piecewise linear degradation modeling)
        if self.rul_cap is not None:
            df['RUL_capped'] = df['RUL'].clip(upper=self.rul_cap)
        else:
            df['RUL_capped'] = df['RUL']

        # Failure prediction labels
        df['label_binary'] = (df['RUL'] <= self.w1).astype(int)

        # Multi-class alert status: 0=Normal, 1=Warning (<=30), 2=Critical (<=15)
        df['alert_level'] = 0
        df.loc[df['RUL'] <= self.w1, 'alert_level'] = 1
        df.loc[df['RUL'] <= self.w0, 'alert_level'] = 2

        return df

    def add_labels_test(self, test_df: pd.DataFrame, truth_series: pd.Series) -> pd.DataFrame:
        """Generates ground-truth RUL and labels for test data using truth file."""
        df = test_df.copy()
        last_cycles = df.groupby('unit_id')['cycle'].max().reset_index()
        last_cycles.columns = ['unit_id', 'last_cycle']

        truth_df = pd.DataFrame({
            'unit_id': np.arange(1, len(truth_series) + 1),
            'remaining_truth': truth_series.values
        })
        merged = last_cycles.merge(truth_df, on='unit_id', how='left')
        merged['failure_cycle'] = merged['last_cycle'] + merged['remaining_truth']

        df = df.merge(merged[['unit_id', 'failure_cycle']], on='unit_id', how='left')
        df['RUL'] = df['failure_cycle'] - df['cycle']
        df.drop(columns=['failure_cycle'], inplace=True)

        if self.rul_cap is not None:
            df['RUL_capped'] = df['RUL'].clip(upper=self.rul_cap)
        else:
            df['RUL_capped'] = df['RUL']

        df['label_binary'] = (df['RUL'] <= self.w1).astype(int)
        df['alert_level'] = 0
        df.loc[df['RUL'] <= self.w1, 'alert_level'] = 1
        df.loc[df['RUL'] <= self.w0, 'alert_level'] = 2

        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds rolling temporal features (mean, std) and lag difference features."""
        df_feats = df.copy()
        w = self.rolling_window

        # Operational sensors to create rolling features for
        features_to_roll = [s for s in self.active_sensors]

        rolling_means = []
        rolling_stds = []
        lag_diffs = []

        for unit_id, group in df_feats.groupby('unit_id'):
            # Rolling mean
            rmean = group[features_to_roll].rolling(window=w, min_periods=1).mean()
            rmean.columns = [f'{col}_roll_mean_{w}' for col in features_to_roll]
            rolling_means.append(rmean)

            # Rolling std
            rstd = group[features_to_roll].rolling(window=w, min_periods=1).std().fillna(0)
            rstd.columns = [f'{col}_roll_std_{w}' for col in features_to_roll]
            rolling_stds.append(rstd)

            # Lag difference (rate of change over 3 cycles)
            ldiff = group[features_to_roll].diff(periods=3).fillna(0)
            ldiff.columns = [f'{col}_lag_diff_3' for col in features_to_roll]
            lag_diffs.append(ldiff)

        df_means = pd.concat(rolling_means).sort_index()
        df_stds = pd.concat(rolling_stds).sort_index()
        df_lags = pd.concat(lag_diffs).sort_index()

        df_out = pd.concat([df_feats, df_means, df_stds, df_lags], axis=1)
        return df_out

    def fit_transform(
        self,
        val_engine_ratio: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List[str]]:
        """
        Fits scaler on training engines (with engine-level train/validation split to avoid leakage)
        and transforms train, val, and test data.
        Returns:
            train_df, val_df, test_df, feature_cols
        """
        raw_train = self.load_raw(self.train_path)
        raw_test = self.load_raw(self.test_path)
        truth_series = pd.read_csv(self.truth_path, sep=r'\s+', header=None).iloc[:, 0]

        # 1. Denoising with Kalman Filter
        if self.use_kalman:
            raw_train = apply_kalman_smoothing(raw_train, self.active_sensors)
            raw_test = apply_kalman_smoothing(raw_test, self.active_sensors)

        # 2. Operating condition regime clustering (if multi-condition)
        if self.dataset_name in ['FD002', 'FD004']:
            raw_train['regime'] = self.compute_regimes(raw_train, fit=True)
            raw_test['regime'] = self.compute_regimes(raw_test, fit=False)

        # 3. Add ground truth labels
        train_labeled = self.add_labels_train(raw_train)
        test_labeled = self.add_labels_test(raw_test, truth_series)

        # 4. Feature engineering
        train_fe = self.engineer_features(train_labeled)
        test_fe = self.engineer_features(test_labeled)

        # Define candidate features
        exclude_cols = ['unit_id', 'cycle', 'RUL', 'RUL_capped', 'label_binary', 'alert_level']
        if self.dataset_name in ['FD002', 'FD004']:
            exclude_cols.append('regime')
        self.feature_cols = [c for c in train_fe.columns if c not in exclude_cols]

        # 5. Engine-level split (NO LEAKAGE)
        unique_engines = train_fe['unit_id'].unique()
        np.random.seed(random_state)
        shuffled_engines = np.random.permutation(unique_engines)
        n_val = int(len(unique_engines) * val_engine_ratio)
        val_engines = set(shuffled_engines[:n_val])
        train_engines = set(shuffled_engines[n_val:])

        train_split = train_fe[train_fe['unit_id'].isin(train_engines)].copy()
        val_split = train_fe[train_fe['unit_id'].isin(val_engines)].copy()
        test_split = test_fe.copy()

        # 6. Fit scaler on training engines ONLY
        self.scaler.fit(train_split[self.feature_cols])

        # Transform features
        train_split[self.feature_cols] = self.scaler.transform(train_split[self.feature_cols])
        val_split[self.feature_cols] = self.scaler.transform(val_split[self.feature_cols])
        test_split[self.feature_cols] = self.scaler.transform(test_split[self.feature_cols])

        self.is_fitted = True

        return train_split, val_split, test_split, self.feature_cols

    def save_artifacts(self, output_dir: str):
        """Saves fitted scaler, feature columns, and dataset configuration."""
        os.makedirs(output_dir, exist_ok=True)
        joblib.dump(self.scaler, os.path.join(output_dir, f'{self.dataset_name}_scaler.joblib'))
        meta = {
            'dataset_name': self.dataset_name,
            'rul_cap': self.rul_cap,
            'early_failure_window': self.w1,
            'warning_window': self.w0,
            'use_kalman': self.use_kalman,
            'scale_type': self.scale_type,
            'constant_sensors': self.constant_sensors,
            'active_sensors': self.active_sensors,
            'feature_cols': self.feature_cols
        }
        with open(os.path.join(output_dir, f'{self.dataset_name}_preprocessor_meta.json'), 'w') as f:
            json.dump(meta, f, indent=2)


def generate_sequences(
    df: pd.DataFrame,
    feature_cols: List[str],
    seq_length: int = 30,
    target_col: str = 'RUL_capped',
    last_only: bool = False
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generates 3D sliding sequence arrays (samples, seq_length, features) for PyTorch LSTM models.
    If last_only is True, extracts only the last sequence per engine (standard for test evaluation).
    """
    sequences = []
    targets = []
    unit_ids = []

    for unit_id, group in df.groupby('unit_id'):
        data_matrix = group[feature_cols].values
        target_array = group[target_col].values
        n_cycles = len(data_matrix)

        if n_cycles < seq_length:
            # Pad beginning with first cycle values
            pad_len = seq_length - n_cycles
            pad_features = np.repeat(data_matrix[:1], pad_len, axis=0)
            data_matrix = np.vstack([pad_features, data_matrix])
            pad_targets = np.repeat(target_array[:1], pad_len, axis=0)
            target_array = np.concatenate([pad_targets, target_array])
            n_cycles = seq_length

        if last_only:
            sequences.append(data_matrix[-seq_length:])
            targets.append(target_array[-1])
            unit_ids.append(unit_id)
        else:
            for i in range(seq_length, n_cycles + 1):
                sequences.append(data_matrix[i - seq_length:i])
                targets.append(target_array[i - 1])
                unit_ids.append(unit_id)

    return (
        np.array(sequences, dtype=np.float32),
        np.array(targets, dtype=np.float32),
        np.array(unit_ids, dtype=np.int32)
    )
