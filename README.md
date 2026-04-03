# 🐸 thefrogpit

**A self-hosted home-lab monitoring and automation platform.** thefrogpit runs a suite of lightweight Python agents that continuously watch over services, sensors, backups, and security — sending real-time push notifications via [ntfy.sh](https://ntfy.sh) when anything needs attention.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Scripts](#scripts)
- [Agents](#agents)
- [Setup](#setup)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Planning](#planning)
- [Contributing](#contributing)

---

## Overview

thefrogpit is the home-lab server hosting:

| Service | Description |
|---|---|
| **WordPress** | Personal site at [averyizatt.com](https://averyizatt.com) |
| **Frog Tank API** | Flask API for ESP32 temperature/humidity sensors |
| **Plex** | Media server |
| **Dashboard** | Homer-based admin dashboard |

A second node (**thebrain**) runs the AI agent orchestration layer so monitoring workloads never impact the main server's performance.

All agents write structured JSON logs to a shared log file and push alerts to an NTFY topic (`thefrogpit`) for real-time mobile notifications.

---

## Project Structure

```
thefrogpit/
├── Agents/                   # Agent orchestration config and reasoning engine
│   ├── AutoGen.yaml          # AutoGen agent schedule definitions
│   └── reasoningAgent.py     # LLM-powered autonomous DevOps reasoning agent
├── Planning/                 # Architecture docs and integration plans
│   └── mcpIntegrationPlan.txt
├── Scripts/                  # Monitoring agents (run on a schedule via cron/AutoGen)
│   ├── status_logger.py      # Shared structured JSON logger used by all agents
│   ├── HealthCheckerAgent.py # Web uptime + SSL certificate monitor
│   ├── SecurityWatchDogAgent.py # SSH auth log scanner for failed login attempts
│   ├── SensorSanityAgent.py  # Frog tank temp/humidity threshold checker
│   ├── backUpVerifier.py     # Verifies backup archives exist on disk
│   ├── diskUsageMonitor.py   # Alerts when disk usage exceeds threshold
│   ├── reDisSub.py           # Redis pub/sub event subscriber
│   └── sslExpiry.py          # Standalone SSL certificate expiry checker
└── requirements.txt          # Python dependencies
```

---

## Scripts

All scripts share a common pattern:
- Import `status_logger.log_status` to write structured JSON entries to a shared log.
- Post push notifications to NTFY when an alert condition is detected.
- Can be run standalone or orchestrated via `AutoGen.yaml`.

### `HealthCheckerAgent.py`
Polls HTTP endpoints and checks SSL certificate validity for `averyizatt.com`. Alerts if any endpoint returns a non-200 status or if the SSL certificate expires within 30 days.

**Monitored endpoints:**
- `https://averyizatt.com/frogtank/health` (Frog Tank API)
- `https://averyizatt.com` (WordPress)

### `SecurityWatchDogAgent.py`
Scans the last 100 lines of `/var/log/auth.log` for patterns indicating brute-force or unauthorized SSH login attempts. Sends an NTFY alert for each match found.

**Detected patterns:** `Failed password`, `Invalid user`, `authentication failure`

### `SensorSanityAgent.py`
Reads the latest CSV log entry from each frog tank sensor. Compares temperature and humidity against configured safe ranges and alerts when values drift out of bounds.

**Default thresholds:**
- Temperature: 60–85 °F
- Humidity: 40–80 %

### `backUpVerifier.py`
Checks that all expected backup files (`db.sql`, `site.tar.gz`) exist in the backup directory. Alerts if any file is missing.

### `diskUsageMonitor.py`
Checks root filesystem usage. Sends an alert when usage exceeds the configured threshold (default: 90%).

### `reDisSub.py`
Subscribes to the `agents` Redis pub/sub channel and logs any messages received. Useful for cross-agent event signalling.

### `sslExpiry.py`
Standalone SSL certificate expiry checker for `averyizatt.com`. Warns when fewer than 30 days remain before expiry.

### `status_logger.py`
Shared utility used by all agents. Appends structured JSON log entries (timestamp, agent name, level, message) to `/mnt/shared/agent-status.json`.

---

## Agents

### `Agents/AutoGen.yaml`
Defines the agent schedule for the AutoGen orchestrator running on **thebrain**. Each agent entry specifies:
- `name` — human-readable agent label
- `task` — description of what the agent does
- `command` — SSH command that runs the script on the target server
- `interval` — how often the agent fires (e.g., `5m`, `1h`, `24h`)

### `Agents/reasoningAgent.py`
An advanced autonomous reasoning agent powered by a locally-hosted [Ollama](https://ollama.com) LLM (default model: `mistral`). It:
1. Reads recent agent status logs and persistent memory.
2. Queries an LLM to decide what action to take next.
3. Optionally writes a new agent script (after syntax validation) or appends a new AutoGen config entry.
4. Persists its reasoning memory for future runs.

---

## Setup

### Prerequisites

- Python 3.9+
- Redis (for `reDisSub.py`)
- Access to `/var/log/auth.log` (for `SecurityWatchDogAgent.py`)
- An [ntfy.sh](https://ntfy.sh) account or self-hosted ntfy instance
- Ollama with `mistral` model pulled (for `reasoningAgent.py` only)

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

All configuration is done via constants at the top of each script. Key values to update before first run:

| Variable | Script | Description |
|---|---|---|
| `NTFY_TOPIC` | All scripts | Your ntfy topic name |
| `ENDPOINTS` | `HealthCheckerAgent.py` | URLs to health-check |
| `hostname` | `HealthCheckerAgent.py`, `sslExpiry.py` | Domain to check SSL for |
| `AUTH_LOG` | `SecurityWatchDogAgent.py` | Path to auth log |
| `LOGDIR` | `SensorSanityAgent.py` | Path to sensor CSV logs |
| `BACKUP_DIR` | `backUpVerifier.py` | Path to backup directory |
| `THRESHOLD` | `diskUsageMonitor.py` | Disk usage alert threshold (%) |
| `TEMP_THRESHOLDS` | `SensorSanityAgent.py` | Safe temperature range (°F) |
| `HUMIDITY_THRESHOLDS` | `SensorSanityAgent.py` | Safe humidity range (%) |
| `OLLAMA_URL` | `reasoningAgent.py` | Ollama API endpoint |

---

## Deployment

### Running a Script Manually

```bash
python3 Scripts/HealthCheckerAgent.py
```

### Scheduling with Cron

Example crontab entries:

```cron
*/5 * * * *  python3 /home/frogadmin/agent-scripts/HealthCheckerAgent.py
*/5 * * * *  python3 /home/frogadmin/agent-scripts/SecurityWatchDogAgent.py
*/5 * * * *  python3 /home/frogadmin/agent-scripts/SensorSanityAgent.py
*/10 * * * * python3 /home/frogadmin/agent-scripts/diskUsageMonitor.py
0 */12 * * * python3 /home/frogadmin/agent-scripts/sslExpiry.py
0 2 * * *    python3 /home/frogadmin/agent-scripts/backUpVerifier.py
```

### Scheduling with AutoGen (Recommended)

Deploy `Agents/AutoGen.yaml` on **thebrain** and point AutoGen at the YAML config. Agents will be dispatched via SSH on their configured intervals.

---

## Planning

See [`Planning/mcpIntegrationPlan.txt`](Planning/mcpIntegrationPlan.txt) for the full roadmap covering:

- Phase 1: Setting up the second ThinkCentre node (thebrain)
- Phase 2: Deploying the AutoGen/CrewAI control server
- Phase 3: First agent implementations
- Phase 4: Agent orchestration chains
- Phase 5: Dashboard integration
- Phase 6: LLM-powered predictive automation

---

## Contributing

This is a personal home-lab project. If you want to suggest an improvement or report a bug, please open an [issue](https://github.com/averyizatt/thefrogpit/issues). Pull requests are welcome for bug fixes or new monitoring agents.
