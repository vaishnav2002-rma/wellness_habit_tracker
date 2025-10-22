# app/utils/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Timezone
IST = pytz.timezone("Asia/Kolkata")

# Twilio setup
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize scheduler
scheduler = BackgroundScheduler(timezone=IST)


def send_reminder(reminder_id: str, title: str, user_id: str, reminder_time: str):
    """Triggered by APScheduler at reminder_time"""
    message_body = f"🔔 *Reminder Alert!*\n\nTitle: {title}\nTime: {reminder_time}\nStay consistent with your habits! 💪"

    try:
        client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=MY_WHATSAPP_NUMBER,
            body=message_body
        )
        print(f"[✅ WhatsApp Reminder Sent] {datetime.now(IST)} | User: {user_id} | Title: {title}")

    except Exception as e:
        print(f"[❌ Error Sending WhatsApp Message]: {e}")


def schedule_reminder(reminder_id: str, title: str, user_id: str, reminder_time: datetime):
    """Schedules a one-time WhatsApp reminder"""
    scheduler.add_job(
        send_reminder,
        "date",
        run_date=reminder_time,
        args=[reminder_id, title, user_id, reminder_time.isoformat()],
        id=reminder_id,
        replace_existing=True
    )
    print(f"[📅 Reminder Scheduled] ID: {reminder_id} | Time: {reminder_time}")


# Start scheduler
scheduler.start()

