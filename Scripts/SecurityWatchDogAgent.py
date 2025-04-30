# security_watchdog_agent.py
# Improved agent that logs structured alerts, supports future learning logic

import re
import requests
from status_logger import log_status
from datetime import datetime

AUTH_LOG = "/var/log/auth.log"
NTFY_TOPIC = "thefrogpit"
BAD_PATTERNS = ["Failed password", "Invalid user", "authentication failure"]

def send_ntfy(message):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode("utf-8"))
    except Exception as e:
        print("Failed to send NTFY:", e)

try:
    with open(AUTH_LOG) as f:
        lines = f.readlines()[-100:]
        for line in lines:
            if any(pat in line for pat in BAD_PATTERNS):
                alert_msg = f"SECURITY ALERT: {line.strip()}"
                send_ntfy(alert_msg)
                log_status("SecurityWatchdog", "ALERT", alert_msg)
except Exception as e:
    log_status("SecurityWatchdog", "ERROR", f"auth.log scan failed: {str(e)}")
