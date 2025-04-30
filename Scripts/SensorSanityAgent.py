# sensor_sanity_agent.py
# Checks frog tank sensor logs for temperature and humidity issues.

import csv
from pathlib import Path
import requests
from status_logger import log_status  # Logging to shared JSON log

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

            temp_issue = not (TEMP_THRESHOLDS[0] <= temp <= TEMP_THRESHOLDS[1])
            hum_issue = not (HUMIDITY_THRESHOLDS[0] <= humidity <= HUMIDITY_THRESHOLDS[1])

            if temp_issue:
                msg = f"{sensor} TEMP out of range: {temp}"
                send_ntfy(f"ALERT: {msg}")
                log_status("SensorSanity", "ALERT", msg)

            if hum_issue:
                msg = f"{sensor} HUMIDITY out of range: {humidity}"
                send_ntfy(f"ALERT: {msg}")
                log_status("SensorSanity", "ALERT", msg)

            if not temp_issue and not hum_issue:
                log_status("SensorSanity", "OK", f"{sensor}: temp={temp}, humidity={humidity}")

    except Exception as e:
        log_status("SensorSanity", "ERROR", f"{sensor_file.name} failed to parse: {str(e)}")
