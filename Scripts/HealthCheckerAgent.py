import requests
import ssl
import socket
from datetime import datetime

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
            send_ntfy(f"ALERT: {name} is DOWN! Status: {r.status_code}")
    except Exception as e:
        send_ntfy(f"ALERT: {name} is UNREACHABLE! Error: {str(e)}")

hostname = "averyizatt.com"
port = 443
context = ssl.create_default_context()
with socket.create_connection((hostname, port)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        cert = ssock.getpeercert()
        exp_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
        days_left = (exp_date - datetime.utcnow()).days
        if days_left < 30:
            send_ntfy(f"WARNING: SSL Certificate for {hostname} expires in {days_left} days!")

# Managed by: Web Health Monitor Agent (under AutoGen "ServiceMonitor" group)