"""
Dataset Profiling and Exploratory Data Analysis for NASA C-MAPSS (FD001 to FD004)
Analyzes:
1. Engine and cycle distributions
2. Operational settings and operating regimes
3. Constant / zero-variance sensors
4. Sensor correlations and degradation trends
5. Outliers and distribution summaries across FD001 - FD004
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

DATASET_DIR = r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\ml\datasets"

COLUMNS = ['unit_id', 'cycle', 'setting1', 'setting2', 'setting3'] + [f's{i}' for i in range(1, 22)]
SETTINGS = ['setting1', 'setting2', 'setting3']
SENSORS = [f's{i}' for i in range(1, 22)]

DATASET_CONFIGS = {
    'FD001': {
        'train': os.path.join(DATASET_DIR, 'dataset1', 'data', 'train_01.txt'),
        'test': os.path.join(DATASET_DIR, 'dataset1', 'data', 'test_01.txt'),
        'truth': os.path.join(DATASET_DIR, 'dataset1', 'data', 'truth_01.txt'),
        'conditions': 'Sea Level (Single Condition)',
        'fault_modes': 'HPC Degradation'
    },
    'FD002': {
        'train': os.path.join(DATASET_DIR, 'dataset2', 'data', 'train_02.txt'),
        'test': os.path.join(DATASET_DIR, 'dataset2', 'data', 'test_02.txt'),
        'truth': os.path.join(DATASET_DIR, 'dataset2', 'data', 'truth_02.txt'),
        'conditions': 'Six Operating Conditions',
        'fault_modes': 'HPC Degradation'
    },
    'FD003': {
        'train': os.path.join(DATASET_DIR, 'dataset3', 'data', 'train_03.txt'),
        'test': os.path.join(DATASET_DIR, 'dataset3', 'data', 'test_03.txt'),
        'truth': os.path.join(DATASET_DIR, 'dataset3', 'data', 'truth_03.txt'),
        'conditions': 'Sea Level (Single Condition)',
        'fault_modes': 'HPC & Fan Degradation'
    },
    'FD004': {
        'train': os.path.join(DATASET_DIR, 'dataset4', 'data', 'train_04.txt'),
        'test': os.path.join(DATASET_DIR, 'dataset4', 'data', 'test_04.txt'),
        'truth': os.path.join(DATASET_DIR, 'dataset4', 'data', 'truth_04.txt'),
        'conditions': 'Six Operating Conditions',
        'fault_modes': 'HPC & Fan Degradation'
    }
}


def load_raw_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, sep=r'\s+', header=None)
    # The file may contain 26 or more columns; take the first 26
    df = df.iloc[:, :26]
    df.columns = COLUMNS
    return df


def load_truth(filepath: str) -> pd.Series:
    truth = pd.read_csv(filepath, sep=r'\s+', header=None)
    return truth.iloc[:, 0]


def profile_dataset(name: str, cfg: dict) -> dict:
    train_df = load_raw_data(cfg['train'])
    test_df = load_raw_data(cfg['test'])
    truth_series = load_truth(cfg['truth'])

    train_engines = int(train_df['unit_id'].nunique())
    test_engines = int(test_df['unit_id'].nunique())
    total_train_rows = int(len(train_df))
    total_test_rows = int(len(test_df))

    # Engine lifetime distribution (train is run-to-failure)
    train_lifetimes = train_df.groupby('unit_id')['cycle'].max()
    min_life, max_life, mean_life = int(train_lifetimes.min()), int(train_lifetimes.max()), float(train_lifetimes.mean())

    # Detect constant or zero-variance sensors
    sensor_stds = train_df[SENSORS].std()
    constant_sensors = sensor_stds[sensor_stds < 1e-4].index.tolist()
    active_sensors = [s for s in SENSORS if s not in constant_sensors]

    # Sensor correlation with cycle (degradation indicator)
    correlations = {}
    for s in active_sensors:
        corr = float(train_df['cycle'].corr(train_df[s]))
        correlations[s] = round(corr, 4)

    # Sort sensors by absolute correlation with cycle
    sorted_sensors_by_degradation = sorted(
        correlations.items(), key=lambda x: abs(x[1]), reverse=True
    )

    # Operating conditions detection: number of clusters / unique combinations
    # Round settings to 2 decimal places to cluster operating points
    rounded_settings = train_df[SETTINGS].round(2)
    operating_modes = int(rounded_settings.drop_duplicates().shape[0])

    profile = {
        'dataset': name,
        'description': f"{cfg['conditions']} | Fault: {cfg['fault_modes']}",
        'train_engines': train_engines,
        'test_engines': test_engines,
        'train_records': total_train_rows,
        'test_records': total_test_rows,
        'lifetime_min': min_life,
        'lifetime_max': max_life,
        'lifetime_mean': round(mean_life, 1),
        'operating_modes_detected': operating_modes,
        'constant_sensors': constant_sensors,
        'active_sensors_count': len(active_sensors),
        'top_degradation_sensors': sorted_sensors_by_degradation[:6],
        'test_truth_mean_rul': round(float(truth_series.mean()), 1),
        'test_truth_min_rul': int(truth_series.min()),
        'test_truth_max_rul': int(truth_series.max())
    }
    return profile


def run_full_eda():
    results = {}
    print("=" * 70)
    print("PREDIXAI - NASA C-MAPSS DATASET MULTI-SUBSET PROFILING")
    print("=" * 70)

    for name, cfg in DATASET_CONFIGS.items():
        print(f"\n[+] Profiling {name} ({cfg['conditions']})...")
        prof = profile_dataset(name, cfg)
        results[name] = prof
        print(f"    Train Engines: {prof['train_engines']} ({prof['train_records']} rows)")
        print(f"    Test Engines:  {prof['test_engines']} ({prof['test_records']} rows)")
        print(f"    Engine Lifetime: Min {prof['lifetime_min']} - Max {prof['lifetime_max']} (Avg: {prof['lifetime_mean']} cycles)")
        print(f"    Operating Regimes: {prof['operating_modes_detected']}")
        print(f"    Constant (Zero-variance) Sensors: {prof['constant_sensors']}")
        print(f"    Top Degradation Correlated Sensors: {prof['top_degradation_sensors']}")

    # Save summary to JSON
    out_path = r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\ml\experiments\eda_summary.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 70)
    print(f"[SUCCESS] EDA profiling report saved to: {out_path}")
    print("=" * 70)


if __name__ == '__main__':
    run_full_eda()
