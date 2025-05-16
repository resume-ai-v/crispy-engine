import os
import time
from datetime import datetime
from pathlib import Path

TMP_DIR = "/tmp/career_ai_vault"
ARCHIVE_DIR = "data/resume_archive"
TMP_EXPIRY_HOURS = 48
ARCHIVE_EXPIRY_DAYS = 60

def ensure_dirs():
    Path(TMP_DIR).mkdir(parents=True, exist_ok=True)
    Path(ARCHIVE_DIR).mkdir(parents=True, exist_ok=True)

def timestamped_filename(role: str, company: str, file_type: str) -> str:
    now = datetime.now().strftime("%Y-%m-%dT%H-%M")
    return f"{file_type}_{role}_{company}_{now}.pdf".replace(" ", "_")

def save_temp_file(content: bytes, role: str, company: str, file_type: str):
    ensure_dirs()
    filename = timestamped_filename(role, company, file_type)
    tmp_path = os.path.join(TMP_DIR, filename)
    archive_path = os.path.join(ARCHIVE_DIR, filename)

    with open(tmp_path, "wb") as f:
        f.write(content)
    with open(archive_path, "wb") as f:
        f.write(content)

    print(f"✅ Saved to TMP: {tmp_path}")
    print(f"📦 Backed up to ARCHIVE: {archive_path}")
    return filename

def clean_old_files():
    ensure_dirs()
    now = time.time()

    for file in os.listdir(TMP_DIR):
        path = os.path.join(TMP_DIR, file)
        if os.path.isfile(path) and now - os.path.getmtime(path) > TMP_EXPIRY_HOURS * 3600:
            os.remove(path)
            print(f"🧹 Deleted expired TMP file: {file}")

    for file in os.listdir(ARCHIVE_DIR):
        path = os.path.join(ARCHIVE_DIR, file)
        if os.path.isfile(path) and now - os.path.getmtime(path) > ARCHIVE_EXPIRY_DAYS * 86400:
            os.remove(path)
            print(f"🧼 Deleted ARCHIVED file: {file}")

def get_temp_files():
    ensure_dirs()
    files = []
    for fname in os.listdir(TMP_DIR):
        path = os.path.join(TMP_DIR, fname)
        if os.path.isfile(path):
            modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
            files.append({"name": fname, "path": path, "modified": modified})
    return sorted(files, key=lambda x: x["modified"], reverse=True)

def delete_temp_file(filename: str):
    path = os.path.join(TMP_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ Deleted file: {filename}")

def load_temp_file(filename: str) -> bytes:
    path = os.path.join(TMP_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    return b""

# ----------------------------------
# ✅ RESUME APPLICATION LOGGING (add to utils/system/temp_storage_manager.py or logger.py)
# ----------------------------------

import csv
from datetime import datetime

LOG_PATH = "data/application_log.csv"

def log_application(filename: str, job_title: str, company: str):
    os.makedirs("data", exist_ok=True)
    with open(LOG_PATH, mode="a", newline="") as log:
        writer = csv.writer(log)
        writer.writerow([datetime.now().isoformat(), filename, job_title, company])

# Usage:
# log_application(filename="resume_data_analyst.pdf", job_title="Data Analyst", company="Spotify")


# ----------------------------------
# ✅ CRON/Task Setup Instructions
# ----------------------------------

# macOS:
# Run `crontab -e` and add:
# 0 */6 * * * /usr/bin/python3 /Users/you/path/to/auto_cleanup_runner.py

# Windows:
# Task Scheduler > New Task > Trigger every 6 hours
# Action: Run `python auto_cleanup_runner.py`

# Linux:
# crontab -e → same as macOS

