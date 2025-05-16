import os
import time
from datetime import datetime

FOLDER = os.path.expanduser("~/CareerAI-Downloads")  # Custom local folder
EXPIRY_HOURS = 48


def auto_cleanup():
    """Deletes local files older than EXPIRY_HOURS."""
    if not os.path.exists(FOLDER):
        print(f"📂 Folder not found: {FOLDER}")
        return

    now = time.time()
    deleted = 0

    for fname in os.listdir(FOLDER):
        path = os.path.join(FOLDER, fname)
        if os.path.isfile(path):
            modified = os.path.getmtime(path)
            age = (now - modified) / 3600
            if age > EXPIRY_HOURS:
                os.remove(path)
                print(f"🧹 Deleted expired file: {fname}")
                deleted += 1

    if deleted == 0:
        print("✅ No expired files found.")


if __name__ == "__main__":
    auto_cleanup()
