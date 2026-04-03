# disk_usage_monitor.py
# Checks root filesystem usage and alerts when it exceeds the configured threshold.

import shutil

import requests

from status_logger import log_status

THRESHOLD = 90  # Alert when disk usage exceeds this percentage
NTFY_TOPIC = "thefrogpit"
AGENT = "DiskUsageMonitor"


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


def check_disk_usage() -> None:
    """Read root filesystem usage and alert if it is above THRESHOLD."""
    usage = shutil.disk_usage("/")
    percent = int((usage.used / usage.total) * 100)
    if percent > THRESHOLD:
        msg = f"Disk usage alert: {percent}% full!"
        send_ntfy(f"ALERT: {msg}")
        log_status(AGENT, "ALERT", msg)
    else:
        log_status(AGENT, "OK", f"Disk usage at {percent}%")


if __name__ == "__main__":
    check_disk_usage()