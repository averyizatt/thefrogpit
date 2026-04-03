# backup_verifier.py
# Verifies that all expected backup files are present in the backup directory.
# Sends an NTFY alert listing any missing files.

import os
from datetime import datetime, timezone

import requests

from status_logger import log_status

BACKUP_DIR = "/media/thefrogpit/SSD 128GB Backup/wordpress"
NTFY_TOPIC = "thefrogpit"
AGENT = "BackupVerifier"
REQUIRED_FILES = ["db.sql", "site.tar.gz"]


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


def verify_backups() -> None:
    """Check that all required backup files exist on disk."""
    missing = [
        f for f in REQUIRED_FILES
        if not os.path.exists(os.path.join(BACKUP_DIR, f))
    ]

    if not missing:
        log_status(AGENT, "OK", "All required backup files found.")
    else:
        msg = (
            f"Backup check failed at {datetime.now(timezone.utc).isoformat()}! "
            f"Missing: {', '.join(missing)}"
        )
        send_ntfy(f"ALERT: {msg}")
        log_status(AGENT, "ALERT", msg)


if __name__ == "__main__":
    verify_backups()
