# security_watchdog_agent.py
# Scans the SSH auth log for failed login attempts and brute-force patterns.
# Sends a push notification for each suspicious line found.

import requests

from status_logger import log_status

AUTH_LOG = "/var/log/auth.log"
NTFY_TOPIC = "thefrogpit"
AGENT = "SecurityWatchdog"
BAD_PATTERNS = ["Failed password", "Invalid user", "authentication failure"]
SCAN_LINES = 100


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


def scan_auth_log() -> None:
    """Check the last SCAN_LINES lines of the auth log for suspicious entries."""
    try:
        with open(AUTH_LOG) as f:
            lines = f.readlines()[-SCAN_LINES:]
        for line in lines:
            if any(pat in line for pat in BAD_PATTERNS):
                alert_msg = f"SECURITY ALERT: {line.strip()}"
                send_ntfy(alert_msg)
                log_status(AGENT, "ALERT", alert_msg)
    except Exception as e:
        log_status(AGENT, "ERROR", f"auth.log scan failed: {e}")


if __name__ == "__main__":
    scan_auth_log()
