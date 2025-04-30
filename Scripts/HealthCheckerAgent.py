# health_checker_agent.py
# Improved version with structured logging and reasoning stub

import requests
import ssl
import socket
from datetime import datetime
from status_logger import log_status

ENDPOINTS = {
    "frog-api": "https://averyizatt.com/frogtank/health",
    "wordpress": "https://averyizatt.com"
}
NTFY_TOPIC = "thefrogpit"


def send_ntfy(message):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode("utf-8"))
    except Exception as e:
        print("Failed to send NTFY:", e)


for name, url in ENDPOINTS.items():
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            msg = f"{name} is DOWN! Status: {r.status_code}"
            send_ntfy(f"ALERT: {msg}")
            log_status("WebHealthMonitor", "ALERT", msg)
        else:
            log_status("WebHealthMonitor", "OK", f"{name} responded 200 OK")
    except Exception as e:
        msg = f"{name} unreachable: {str(e)}"
        send_ntfy(f"ALERT: {msg}")
        log_status("WebHealthMonitor", "ERROR", msg)


# SSL Certificate Check
hostname = "averyizatt.com"
port = 443
context = ssl.create_default_context()
try:
    with socket.create_connection((hostname, port), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            exp_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
            days_left = (exp_date - datetime.utcnow()).days
            if days_left < 30:
                msg = f"SSL Certificate for {hostname} expires in {days_left} days!"
                send_ntfy(f"WARNING: {msg}")
                log_status("WebHealthMonitor", "WARNING", msg)
            else:
                log_status("WebHealthMonitor", "OK", f"SSL cert valid: {days_left} days left")
except Exception as e:
    msg = f"SSL check error: {str(e)}"
    log_status("WebHealthMonitor", "ERROR", msg)
