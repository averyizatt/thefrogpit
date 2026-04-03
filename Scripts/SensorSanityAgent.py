# sensor_sanity_agent.py
# Reads the latest CSV entry from each frog tank sensor log and checks whether
# temperature and humidity are within acceptable thresholds.
# Sends NTFY alerts when values drift out of range.

from pathlib import Path

import requests

from status_logger import log_status

LOGDIR = Path("/home/thefrogpit/frog-api/logs")
NTFY_TOPIC = "thefrogpit"
AGENT = "SensorSanity"
# Temperature thresholds in °F
TEMP_MIN, TEMP_MAX = 60, 85
# Humidity thresholds in %
HUMIDITY_MIN, HUMIDITY_MAX = 40, 80


def send_ntfy(message: str) -> None:
    """Post a push notification to the configured NTFY topic."""
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            timeout=10,
        )
    except Exception as e:
        print(f"Failed to send NTFY: {e}")


def check_sensor_file(sensor_file: Path) -> None:
    """Parse the last CSV row in sensor_file and validate thresholds."""
    try:
        with open(sensor_file) as f:
            last_line = f.readlines()[-1]
        parts = last_line.strip().split(",")
        sensor = parts[1]
        temp = float(parts[2])
        humidity = float(parts[3])

        temp_issue = not (TEMP_MIN <= temp <= TEMP_MAX)
        hum_issue = not (HUMIDITY_MIN <= humidity <= HUMIDITY_MAX)

        if temp_issue:
            msg = f"{sensor} TEMP out of range: {temp}"
            send_ntfy(f"ALERT: {msg}")
            log_status(AGENT, "ALERT", msg)

        if hum_issue:
            msg = f"{sensor} HUMIDITY out of range: {humidity}"
            send_ntfy(f"ALERT: {msg}")
            log_status(AGENT, "ALERT", msg)

        if not temp_issue and not hum_issue:
            log_status(AGENT, "OK", f"{sensor}: temp={temp}, humidity={humidity}")

    except Exception as e:
        log_status(AGENT, "ERROR", f"{sensor_file.name} failed to parse: {e}")


def run() -> None:
    """Iterate over all sensor CSV files in LOGDIR."""
    for sensor_file in LOGDIR.glob("*.csv"):
        check_sensor_file(sensor_file)


if __name__ == "__main__":
    run()
