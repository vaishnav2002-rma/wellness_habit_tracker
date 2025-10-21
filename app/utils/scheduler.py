# app/utils/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

scheduler = BackgroundScheduler(timezone=IST)

def send_reminder(reminder_id: str, title: str, user_id: str, reminder_time: str):
    print(f"[🔔 Reminder Triggered] {datetime.now(IST)} | User: {user_id}, Title: {title}, Time: {reminder_time}, ID: {reminder_id}")

def schedule_reminder(reminder_id: str, title: str, user_id: str, reminder_time: datetime):
    # Schedule a one-time job
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=reminder_time,
        args=[reminder_id, title, user_id, reminder_time.isoformat()],
        id=reminder_id,  # unique job ID
        replace_existing=True
    )
    print(f"[✅ Reminder Scheduled] ID: {reminder_id}, Time: {reminder_time}")

# Start scheduler on import
scheduler.start()
