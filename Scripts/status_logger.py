# status_logger.py
# Shared structured JSON logger used by all monitoring agents.
# Appends log entries to a shared JSON file so all agents write to one place.

import json
import os
from datetime import datetime, timezone

STATUS_LOG = os.environ.get("AGENT_STATUS_LOG", "/mnt/shared/agent-status.json")


def log_status(agent: str, level: str, message: str) -> None:
    """Append a structured log entry to the shared agent status log.

    Args:
        agent:   Name of the agent writing the entry (e.g. "DiskUsageMonitor").
        level:   Severity label — one of OK, INFO, WARNING, ALERT, ERROR, MESSAGE.
        message: Human-readable description of the event.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "level": level,
        "message": message,
    }

    # Load existing entries (if any), append, and write back.
    try:
        if os.path.exists(STATUS_LOG):
            with open(STATUS_LOG, "r") as f:
                logs = json.load(f)
        else:
            logs = []
    except (json.JSONDecodeError, OSError):
        logs = []

    logs.append(entry)

    try:
        os.makedirs(os.path.dirname(STATUS_LOG), exist_ok=True)
        with open(STATUS_LOG, "w") as f:
            json.dump(logs, f, indent=2)
    except OSError as e:
        print(f"[status_logger] Failed to write log: {e}")

    print(f"[{entry['timestamp']}] [{agent}] [{level}] {message}")
