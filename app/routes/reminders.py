from fastapi import APIRouter, Depends, HTTPException
from app.models.reminder import ReminderCreate, ReminderResponse
from app.utils.security import get_current_user
from app.database import db
from bson import ObjectId
from datetime import datetime
from app.utils.scheduler import send_reminder_task

router = APIRouter(prefix="/reminders", tags=["Reminders"])

reminders_collection = db["reminders"]

# Create a reminder
@router.post("/", response_model=ReminderResponse)
async def create_reminder(reminder: ReminderCreate, current_user: dict = Depends(get_current_user)):
    new_reminder = {
        "user_id": str(current_user["_id"]),
        "title": reminder.title,
        "reminder_type": reminder.reminder_type,
        "target_id": reminder.target_id,
        "reminder_time": reminder.reminder_time.isoformat(),
        "repeat": reminder.repeat,
        "created_at": datetime.utcnow()
    }
    result = await reminders_collection.insert_one(new_reminder)

    send_reminder_task.apply_async(
        args=[str(result.inserted_id), reminder.title, reminder.reminder_time.isoformat(), str(current_user["_id"])],
        eta=reminder.reminder_time  # Schedule execution
    )

    return ReminderResponse(
        id=str(result.inserted_id),
        user_id=new_reminder["user_id"],
        title=new_reminder["title"],
        reminder_type=new_reminder["reminder_type"],
        target_id=new_reminder["target_id"],
        reminder_time=reminder.reminder_time,
        repeat=new_reminder["repeat"],
        created_at=new_reminder["created_at"]
    )

# Get all reminders for logged-in user
@router.get("/", response_model=list[ReminderResponse])
async def get_reminders(current_user: dict = Depends(get_current_user)):
    cursor = reminders_collection.find({"user_id": str(current_user["_id"])})
    reminders = []
    async for doc in cursor:
        reminders.append(ReminderResponse(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            title=doc["title"],
            reminder_type=doc["reminder_type"],
            target_id=doc.get("target_id"),
            reminder_time=datetime.fromisoformat(doc["reminder_time"]),
            repeat=doc.get("repeat"),
            created_at=doc["created_at"]
        ))
    return reminders

