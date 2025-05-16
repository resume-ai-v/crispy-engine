from apscheduler.schedulers.background import BackgroundScheduler
from jobs.job_fetcher import get_jobs_from_jsearch

scheduler = BackgroundScheduler()


def refresh_jobs():
    print("🔄 Refreshing job listings from JSearch...")
    get_jobs_from_jsearch("Software Engineer")


scheduler.add_job(refresh_jobs, "interval", hours=6)


def start_scheduler():
    scheduler.start()
    print("✅ Job scheduler running...")

