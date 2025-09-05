from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.models.reminder import ReminderCreate, ReminderUpdate, ReminderResponse
from app.utils.security import get_current_user
from app.database import db
from bson import ObjectId
from datetime import datetime
import asyncio
import pytz   # ✅ for timezone

router = APIRouter(prefix="/reminders", tags=["Reminders"])

reminders_collection = db["reminders"]

# Timezone for IST
IST = pytz.timezone("Asia/Kolkata")

# -------------------
# Background function
# -------------------
async def send_reminder(reminder_id: str, title: str, reminder_time: datetime, user_id: str):
    
    if isinstance(reminder_time, str):
        reminder_time = datetime.fromisoformat(reminder_time)
    
    if reminder_time.tzinfo is None:
        reminder_time = IST.localize(reminder_time)

    now = datetime.now(IST)   # ✅ use IST now
    delay = (reminder_time - now).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)

    print(f"[Reminder 🔔] User: {user_id}, Title: {title}, Time: {reminder_time}, ID: {reminder_id}")


# -------------------
# Create reminder
# -------------------
@router.post("/", response_model=ReminderResponse)
async def create_reminder(
    reminder: ReminderCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    new_reminder = {
        "user_id": str(current_user["_id"]),
        "title": reminder.title,
        "reminder_type": reminder.reminder_type,
        "target_id": reminder.target_id,
        "reminder_time": reminder.reminder_time.isoformat(),
        "repeat": reminder.repeat,
        "created_at": datetime.now(IST)   # ✅ store IST time
    }

    result = await reminders_collection.insert_one(new_reminder)

    # ✅ Schedule background task
    background_tasks.add_task(
        send_reminder,
        str(result.inserted_id),
        reminder.title,
        new_reminder["reminder_time"],  # this is already a datetime
        str(current_user["_id"])
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


# -------------------
# Get reminders
# -------------------
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
            created_at=doc["created_at"].astimezone(IST)  # ✅ convert to IST on response
        ))
    return reminders


# -------------------
# Update reminder
# -------------------
@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(reminder_id: str, update_data: ReminderUpdate, current_user: dict = Depends(get_current_user)):
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    reminder = await reminders_collection.find_one_and_update(
        {"_id": ObjectId(reminder_id), "user_id": str(current_user["_id"])},
        {"$set": update_dict},
        return_document=True
    )

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return ReminderResponse(
        id=str(reminder["_id"]),
        user_id=reminder["user_id"],
        title=reminder["title"],
        reminder_type=reminder["reminder_type"],
        target_id=reminder.get("target_id"),
        reminder_time=datetime.fromisoformat(reminder["reminder_time"]) if isinstance(reminder["reminder_time"], str) else reminder["reminder_time"],
        repeat=reminder.get("repeat"),
        created_at=reminder["created_at"].astimezone(IST)  # ✅ convert to IST on response
    )


# -------------------
# Delete reminder
# -------------------
@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: str, current_user: dict = Depends(get_current_user)):
    result = await reminders_collection.delete_one({"_id": ObjectId(reminder_id), "user_id": str(current_user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return {"msg": "Reminder deleted successfully"}
