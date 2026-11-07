"""
MQTT Telemetry Publisher for PredixAI Industrial IoT Integration.
Publishes streaming equipment sensor JSON to Mosquitto / EMQX MQTT broker.
"""

import os
import time
import json
import argparse
import paho.mqtt.client as mqtt
import pandas as pd

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_PREFIX = "factory/turbofan"
DATASET_PATH = os.getenv(
    "SIM_DATASET_PATH",
    r"C:\Users\Dharmesh Verma\.gemini\antigravity\scratch\PredixAI\ml\datasets\dataset1\data\test_01.txt"
)


def run_mqtt_stream(unit_id: int = 1, interval: float = 1.0, broker: str = MQTT_BROKER, port: int = MQTT_PORT):
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=f"sim_eng_{unit_id}")

    try:
        client.connect(broker, port, keepalive=60)
        client.loop_start()
        print(f"[MQTT] Connected to broker {broker}:{port}")
    except Exception as e:
        print(f"[MQTT WARN] Could not connect to MQTT broker at {broker}:{port} ({e}). Running in standalone mock mode.")

    df = pd.read_csv(DATASET_PATH, sep=r'\s+', header=None).iloc[:, :26]
    df.columns = ['unit_id', 'cycle', 'setting1', 'setting2', 'setting3'] + [f's{i}' for i in range(1, 22)]
    engine_data = df[df['unit_id'] == unit_id].sort_values('cycle')

    machine_id = f"ENG-{str(unit_id).zfill(3)}"
    topic = f"{MQTT_TOPIC_PREFIX}/{machine_id}/telemetry"

    for _, row in engine_data.iterrows():
        payload = {
            "machine_id": machine_id,
            "cycle": int(row['cycle']),
            "setting1": float(row['setting1']),
            "setting2": float(row['setting2']),
            "setting3": float(row['setting3']),
            **{f"s{i}": float(row[f"s{i}"]) for i in range(1, 22)},
            "timestamp": time.time()
        }
        msg_str = json.dumps(payload)
        try:
            client.publish(topic, msg_str, qos=1)
            print(f"[MQTT PUB] -> {topic} (Cycle {row['cycle']})")
        except Exception:
            pass
        time.sleep(interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=int, default=1)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    run_mqtt_stream(unit_id=args.engine, interval=args.interval)
