# ssl_expiry_checker.py
# Standalone SSL certificate expiry checker for averyizatt.com.
# Sends an NTFY warning when fewer than SSL_WARN_DAYS remain before expiry.

import ssl
import socket
from datetime import datetime, timezone

import requests

from status_logger import log_status

HOSTNAME = "averyizatt.com"
PORT = 443
SSL_WARN_DAYS = 30
NTFY_TOPIC = "thefrogpit"
AGENT = "SSLExpiryChecker"


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


def check_ssl_expiry() -> None:
    """Connect to HOSTNAME and check how many days remain on its SSL certificate."""
    try:
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        with socket.create_connection((HOSTNAME, PORT), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=HOSTNAME) as ssock:
                cert = ssock.getpeercert()
                exp = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                exp = exp.replace(tzinfo=timezone.utc)
                days = (exp - datetime.now(timezone.utc)).days
                if days < SSL_WARN_DAYS:
                    msg = f"SSL cert for {HOSTNAME} expires in {days} days!"
                    send_ntfy(f"WARNING: {msg}")
                    log_status(AGENT, "WARNING", msg)
                else:
                    log_status(AGENT, "OK", f"SSL valid: {days} days left")
    except Exception as e:
        log_status(AGENT, "ERROR", str(e))


if __name__ == "__main__":
    check_ssl_expiry()
