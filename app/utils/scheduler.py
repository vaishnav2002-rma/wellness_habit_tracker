from app.celery_worker import celery_app
import datetime

@celery_app.task
def send_reminder_task(reminder_id: str, title: str, reminder_time: str, user_id: str):
    # Here you can integrate Email, SMS, Push notifications etc.
    # For now, we just print (or log) it.
    print(f"[Reminder] User: {user_id}, Title: {title}, Scheduled for: {reminder_time}, ID: {reminder_id}")
    return {"status": "sent", "reminder_id": reminder_id, "title": title, "time": reminder_time}
