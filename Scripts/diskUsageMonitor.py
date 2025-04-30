# disk_usage_monitor.py
import shutil, requests
from status_logger import log_status

THRESHOLD = 90  # %
NTFY_TOPIC = "thefrogpit"

def send_ntfy(msg):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode())
    except:
        pass

usage = shutil.disk_usage("/")
percent = int((usage.used / usage.total) * 100)
if percent > THRESHOLD:
    msg = f"Disk usage alert: {percent}% full!"
    send_ntfy(msg)
    log_status("DiskUsageMonitor", "ALERT", msg)
else:
    log_status("DiskUsageMonitor", "OK", f"Disk usage at {percent}%")