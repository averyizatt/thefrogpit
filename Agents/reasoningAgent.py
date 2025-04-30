# reasoning_agent.py (advanced)
# Includes: LLM reasoning, memory, auto-agent creation, validation, feedback loop, and GitHub agent sourcing

import requests
import json
import os
import re
from datetime import datetime
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
STATUS_LOG = "/mnt/shared/agent-status.json"
MEMORY_FILE = "/mnt/shared/reasoning-memory.json"
REASONING_LOG = "/mnt/shared/reasoning.log"
AGENT_CONFIG = "/home/frogadmin/autogen/agent_config.yaml"
AGENT_SCRIPTS_DIR = "/home/frogadmin/agent-scripts"
GITHUB_AGENT_LIST = "https://raw.githubusercontent.com/e2b-dev/awesome-ai-agents/main/README.md"

# Load recent agent logs
try:
    with open(STATUS_LOG, 'r') as f:
        agent_logs = json.load(f)[-10:]
except Exception:
    agent_logs = []

# Load persistent memory
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'r') as f:
        memory = json.load(f)
else:
    memory = {
        "last_actions": [],
        "agent_history": [],
        "ideas": [],
        "failures": []
    }

# Get GitHub agent list for suggestions
try:
    agent_catalog = requests.get(GITHUB_AGENT_LIST).text
    agent_links = re.findall(r'https://github\.com/[\w\-]+/[\w\-]+', agent_catalog)
    agent_refs = list(set(agent_links))[:10]  # only keep 10 for brevity
except Exception:
    agent_refs = []

# Format prompt for Ollama
prompt = f"""
You are an autonomous DevOps reasoning agent. Analyze the logs below and determine what should be done next.

Recent agent logs:
{json.dumps(agent_logs, indent=2)}

Memory of past actions:
{json.dumps(memory['last_actions'], indent=2)}

Known agent failures:
{json.dumps(memory['failures'], indent=2)}

Useful agent libraries:
{json.dumps(agent_refs, indent=2)}

Return a plan, optional agent script, and config block.
Output format:
<PLAN>Summary of action</PLAN>
<SCRIPT filename="example.py">...python code...</SCRIPT>
<CONFIG name="ExampleAgent">...yaml config block...</CONFIG>
"""

try:
    res = requests.post(OLLAMA_URL, json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    result = res.json().get("response", "")

    with open(REASONING_LOG, 'a') as log:
        log.write(f"\n[{datetime.now().isoformat()}] Response:\n{result}\n")

    if "<PLAN>" in result:
        plan = result.split("<PLAN>")[1].split("</PLAN>")[0].strip()
        memory['last_actions'].append({"timestamp": datetime.now().isoformat(), "plan": plan})

    if "<SCRIPT" in result:
        filename = result.split('filename="')[1].split('"')[0]
        script = result.split("<SCRIPT filename=\"")[1].split("</SCRIPT>")[0].split(">", 1)[1].strip()
        filepath = Path(AGENT_SCRIPTS_DIR) / filename

        # Validate syntax before saving
        try:
            compile(script, filename, 'exec')
            with open(filepath, 'w') as f:
                f.write(script)
            memory['agent_history'].append(filename)
        except Exception as ve:
            memory['failures'].append({"agent": filename, "error": str(ve)})

    if "<CONFIG" in result:
        config_entry = result.split("<CONFIG name=\"")[1].split("</CONFIG>")[0].split(">", 1)[1].strip()
        with open(AGENT_CONFIG, 'a') as cfg:
            cfg.write(f"\n{config_entry}\n")
        memory['ideas'].append(config_entry)

    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

except Exception as e:
    with open(REASONING_LOG, 'a') as log:
        log.write(f"\n[{datetime.now().isoformat()}] ERROR: {str(e)}\n")
