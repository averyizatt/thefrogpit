import csv
from pathlib import Path
import requests

LOGDIR = Path("/home/thefrogpit/frog-api/logs")
NTFY_TOPIC = "thefrogpit"
TEMP_THRESHOLDS = (60, 85)
HUMIDITY_THRESHOLDS = (40, 80)

def send_ntfy(message):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode("utf-8"))
    except Exception as e:
        print("Failed to send NTFY:", e)

for sensor_file in LOGDIR.glob("*.csv"):
    try:
        with open(sensor_file) as f:
            last_line = f.readlines()[-1]
            parts = last_line.strip().split(",")
            sensor = parts[1]
            temp = float(parts[2])
            humidity = float(parts[3])

            if not (TEMP_THRESHOLDS[0] <= temp <= TEMP_THRESHOLDS[1]):
                send_ntfy(f"ALERT: {sensor} TEMP out of range: {temp}")
            if not (HUMIDITY_THRESHOLDS[0] <= humidity <= HUMIDITY_THRESHOLDS[1]):
                send_ntfy(f"ALERT: {sensor} HUMIDITY out of range: {humidity}")
    except Exception as e:
        print("Sensor check error:", e)

# Managed by: Sensor Sanity Agent (under AutoGen "EnvironmentalMonitor" group)