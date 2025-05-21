# utils/system/temp_storage_manager.py

import os
import time
from datetime import datetime

BASE_DIR = "/tmp/career_ai_vault"
os.makedirs(BASE_DIR, exist_ok=True)

def save_temp_file(data: bytes, role: str = "unknown", company: str = "unknown", file_type: str = "resume") -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{role}_{company}_{file_type}_{timestamp}.pdf".replace(" ", "_")
    file_path = os.path.join(BASE_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(data)
    return file_name

def load_temp_file(filename: str) -> bytes:
    path = os.path.join(BASE_DIR, filename)
    with open(path, "rb") as f:
        return f.read()

def save_user_resume(resume_text: str, user_id: str):
    file_path = os.path.join(BASE_DIR, f"{user_id}_resume.txt")
    with open(file_path, "w") as f:
        f.write(resume_text)
    return file_path

def load_user_resume(user_id: str) -> str:
    file_path = os.path.join(BASE_DIR, f"{user_id}_resume.txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return ""

def get_temp_files():
    return os.listdir(BASE_DIR)

def clean_old_files(max_age_hours=48):
    now = time.time()
    for filename in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, filename)
        if os.path.isfile(path) and now - os.path.getmtime(path) > max_age_hours * 3600:
            os.remove(path)
