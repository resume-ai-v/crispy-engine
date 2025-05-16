import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = "jobs/job_cache.json"
DEFAULT_TTL_HOURS = int(os.getenv("JOB_CACHE_TTL", 12))


def clean_job_cache(cache_path=CACHE_FILE, ttl_hours=DEFAULT_TTL_HOURS) -> dict:
    """
    Cleans job cache if it's older than the TTL.

    Returns:
        dict: {status, message}
    """
    if not os.path.exists(cache_path):
        return {"status": "no_cache", "message": "📁 No job cache file found."}

    modified = datetime.fromtimestamp(os.path.getmtime(cache_path))
    age = datetime.now() - modified

    if age > timedelta(hours=ttl_hours):
        os.remove(cache_path)
        return {"status": "cleared", "message": "🧹 Old job cache removed."}
    else:
        return {"status": "valid", "message": f"✅ Job cache valid (age: {int(age.total_seconds()/3600)}h)."}


# Optional CLI entry point for cronjobs or manual cleanup
if __name__ == "__main__":
    result = clean_job_cache()
    print(result["message"])
