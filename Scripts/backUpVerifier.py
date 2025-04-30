# backup_verifier.py
import os, requests
from datetime import datetime
from status_logger import log_status

BACKUP_DIR = "/media/thefrogpit/SSD 128GB Backup/wordpress"
NTFY_TOPIC = "thefrogpit"
required_files = ["db.sql", "site.tar.gz"]
found = all(os.path.exists(os.path.join(BACKUP_DIR, f)) for f in required_files)

if found:
    log_status("BackupVerifier", "OK", "All required backup files found.")
else:
    msg = f"Backup check failed at {datetime.now()}! Missing: {', '.join(f for f in required_files if not os.path.exists(os.path.join(BACKUP_DIR, f)))}"
    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode())
    log_status("BackupVerifier", "ALERT", msg)

