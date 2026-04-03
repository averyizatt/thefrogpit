# health_checker_agent.py
# Polls HTTP endpoints for uptime and checks SSL certificate validity.
# Sends NTFY push notifications on failure or when SSL is expiring soon.

import ssl
import socket
from datetime import datetime, timezone

import requests

from status_logger import log_status

ENDPOINTS = {
    "frog-api": "https://averyizatt.com/frogtank/health",
    "wordpress": "https://averyizatt.com",
}
SSL_HOSTNAME = "averyizatt.com"
SSL_PORT = 443
SSL_WARN_DAYS = 30
NTFY_TOPIC = "thefrogpit"
AGENT = "WebHealthMonitor"


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


def check_endpoints() -> None:
    """Verify each monitored HTTP endpoint returns HTTP 200."""
    for name, url in ENDPOINTS.items():
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                msg = f"{name} is DOWN! Status: {r.status_code}"
                send_ntfy(f"ALERT: {msg}")
                log_status(AGENT, "ALERT", msg)
            else:
                log_status(AGENT, "OK", f"{name} responded 200 OK")
        except Exception as e:
            msg = f"{name} unreachable: {e}"
            send_ntfy(f"ALERT: {msg}")
            log_status(AGENT, "ERROR", msg)


def check_ssl() -> None:
    """Check how many days remain before the SSL certificate expires."""
    context = ssl.create_default_context()
    try:
        with socket.create_connection((SSL_HOSTNAME, SSL_PORT), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=SSL_HOSTNAME) as ssock:
                cert = ssock.getpeercert()
                exp_date = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                exp_date = exp_date.replace(tzinfo=timezone.utc)
                days_left = (exp_date - datetime.now(timezone.utc)).days
                if days_left < SSL_WARN_DAYS:
                    msg = f"SSL Certificate for {SSL_HOSTNAME} expires in {days_left} days!"
                    send_ntfy(f"WARNING: {msg}")
                    log_status(AGENT, "WARNING", msg)
                else:
                    log_status(AGENT, "OK", f"SSL cert valid: {days_left} days left")
    except Exception as e:
        log_status(AGENT, "ERROR", f"SSL check error: {e}")


if __name__ == "__main__":
    check_endpoints()
    check_ssl()
