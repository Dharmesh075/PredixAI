"""
Industrial IoT Sensor Telemetry Simulator for PredixAI.
Streams real-world degradation trajectories from NASA C-MAPSS dataset
into PredixAI REST API and MQTT Broker.
"""

import os
import sys
import time
import json
import argparse
import requests
import pandas as pd
from typing import Optional

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DATASET_PATH = os.getenv(
    "SIM_DATASET_PATH",
    r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\ml\datasets\dataset1\data\test_01.txt"
)

COLUMNS = ['unit_id', 'cycle', 'setting1', 'setting2', 'setting3'] + [f's{i}' for i in range(1, 22)]


class EngineTelemetrySimulator:
    def __init__(self, data_path: str = DATASET_PATH, api_url: str = API_BASE_URL):
        self.data_path = data_path
        self.api_url = api_url
        self.df = None
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.data_path):
            print(f"[WARN] Telemetry data file not found: {self.data_path}")
            return
        df = pd.read_csv(self.data_path, sep=r'\s+', header=None).iloc[:, :26]
        df.columns = COLUMNS
        self.df = df
        print(f"[INFO] Loaded {len(df)} telemetry cycles across {df['unit_id'].nunique()} test engines.")

    def stream_engine(self, unit_id: int = 1, interval_sec: float = 1.0, max_cycles: Optional[int] = None):
        """Simulates continuous live sensor telemetry from a single industrial engine."""
        if self.df is None:
            return

        engine_data = self.df[self.df['unit_id'] == unit_id].sort_values('cycle')
        if len(engine_data) == 0:
            print(f"[ERROR] Engine {unit_id} not found in dataset.")
            return

        machine_id = f"ENG-{str(unit_id).zfill(3)}"
        print(f"\n[STREAMING] Starting live telemetry stream for {machine_id} ({len(engine_data)} cycles available)...")

        cycles_sent = 0
        for _, row in engine_data.iterrows():
            payload = {
                "machine_id": machine_id,
                "cycle": int(row['cycle']),
                "setting1": float(row['setting1']),
                "setting2": float(row['setting2']),
                "setting3": float(row['setting3']),
                **{f"s{i}": float(row[f"s{i}"]) for i in range(1, 22)}
            }

            try:
                endpoint = f"{self.api_url}/api/predict/full"
                resp = requests.post(endpoint, json=payload, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    print(
                        f"  [CYCLE {row['cycle']:>3}] "
                        f"RUL: {data['predicted_rul']:>5.1f} | "
                        f"Fail Prob: {data['failure_probability']:>5.1%} | "
                        f"Health: {data['health_score']:>5.1f}% | "
                        f"Risk: {data['risk_level']:<8} | "
                        f"Anomaly: {data['anomaly_score']:.3f}"
                    )
                else:
                    print(f"  [ERROR] Status {resp.status_code}: {resp.text}")
            except Exception as e:
                print(f"  [CONNECT ERROR] Backend API unreachable at {self.api_url}: {e}")

            cycles_sent += 1
            if max_cycles and cycles_sent >= max_cycles:
                break
            time.sleep(interval_sec)

        print(f"[STREAMING] Telemetry run complete for {machine_id}.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PredixAI Telemetry Simulator")
    parser.add_argument("--engine", type=int, default=1, help="Engine Unit ID (1 to 100)")
    parser.add_argument("--interval", type=float, default=0.5, help="Seconds between cycles")
    parser.add_argument("--cycles", type=int, default=30, help="Max cycles to stream")
    args = parser.parse_args()

    sim = EngineTelemetrySimulator()
    sim.stream_engine(unit_id=args.engine, interval_sec=args.interval, max_cycles=args.cycles)
