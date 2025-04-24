import os
import time
from datetime import datetime, timedelta

STORAGE_DIR = "temp_vault"
EXPIRY_HOURS = 48

def ensure_dir():
    os.makedirs(STORAGE_DIR, exist_ok=True)

def timestamped_filename(role: str, company: str, file_type: str) -> str:
    now = datetime.now().strftime("%Y-%m-%dT%H-%M")
    return f"{file_type}_{role}_{company}_{now}.pdf".replace(" ", "_")

def save_temp_file(content: bytes, role: str, company: str, file_type: str):
    ensure_dir()
    filename = timestamped_filename(role, company, file_type)
    path = os.path.join(STORAGE_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)
    print(f"✅ Saved temporary file: {filename}")
    return filename

def clean_old_files():
    ensure_dir()
    now = time.time()
    expired = 0
    for f in os.listdir(STORAGE_DIR):
        path = os.path.join(STORAGE_DIR, f)
        if os.path.isfile(path):
            if now - os.path.getmtime(path) > EXPIRY_HOURS * 3600:
                os.remove(path)
                expired += 1
    if expired:
        print(f"🧹 Cleaned {expired} expired files from temp vault.")
