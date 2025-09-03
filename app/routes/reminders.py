from fastapi import APIRouter, Depends, HTTPException
from app.models.reminder import ReminderCreate, ReminderUpdate, ReminderResponse
from app.utils.security import get_current_user
from app.database import db
from bson import ObjectId
from datetime import datetime

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

# Update reminder
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
        created_at=reminder["created_at"]
    )

# Delete reminder
@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: str, current_user: dict = Depends(get_current_user)):
    result = await reminders_collection.delete_one({"_id": ObjectId(reminder_id), "user_id": str(current_user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return {"msg": "Reminder deleted successfully"}