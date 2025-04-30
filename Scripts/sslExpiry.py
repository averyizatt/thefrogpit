# ssl_expiry_checker.py
import ssl, socket, requests
from datetime import datetime
from status_logger import log_status

hostname = "averyizatt.com"
NTFY_TOPIC = "thefrogpit"

try:
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            exp = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
            days = (exp - datetime.utcnow()).days
            if days < 30:
                msg = f"SSL cert expires in {days} days!"
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode())
                log_status("SSLExpiryChecker", "WARNING", msg)
            else:
                log_status("SSLExpiryChecker", "OK", f"SSL valid: {days} days left")
except Exception as e:
    log_status("SSLExpiryChecker", "ERROR", str(e))
