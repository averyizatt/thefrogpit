import re
import requests

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
                send_ntfy(f"SECURITY ALERT: {line.strip()}")
except Exception as e:
    print("Security monitor error:", e)

# Managed by: Security Watchdog Agent (under AutoGen "SecurityMonitor" group)