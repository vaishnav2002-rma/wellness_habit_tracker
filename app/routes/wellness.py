from fastapi import APIRouter, Depends, HTTPException
from app.models.wellness import WellnessLogCreate, WellnessLogUpdate, WellnessLogResponse
from app.utils.security import get_current_user
from app.database import db
from bson import ObjectId
from datetime import datetime, date

router = APIRouter(prefix="/wellness/logs", tags=["Wellness"])

wellness_collection = db["wellness_logs"]

# Add wellness log
@router.post("/", response_model=WellnessLogResponse)
async def add_wellness_log(log: WellnessLogCreate, current_user: dict = Depends(get_current_user)):
    today = datetime.utcnow().date()

    # Prevent multiple logs for same user & date
    existing_log = await wellness_collection.find_one({"user_id": str(current_user["_id"]), "date": today.isoformat()})
    if existing_log:
        raise HTTPException(status_code=400, detail="Wellness log for today already exists")

    new_log = {
        "user_id": str(current_user["_id"]),
        "sleep_hours": log.sleep_hours,
        "water_intake_liters": log.water_intake_liters,
        "steps": log.steps,
        "mood": log.mood,
        "date": today.isoformat()
    }
    result = await wellness_collection.insert_one(new_log)

    return WellnessLogResponse(
        id=str(result.inserted_id),
        user_id=new_log["user_id"],
        sleep_hours=new_log["sleep_hours"],
        water_intake_liters=new_log["water_intake_liters"],
        steps=new_log["steps"],
        mood=new_log["mood"],
        date=today
    )

# Get all wellness logs for user
@router.get("/", response_model=list[WellnessLogResponse])
async def get_all_wellness_logs(current_user: dict = Depends(get_current_user)):
    cursor = wellness_collection.find({"user_id": str(current_user["_id"])})
    logs = []
    async for doc in cursor:
        logs.append(WellnessLogResponse(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            sleep_hours=doc["sleep_hours"],
            water_intake_liters=doc["water_intake_liters"],
            steps=doc["steps"],
            mood=doc.get("mood"),
            date=datetime.fromisoformat(doc["date"])
        ))
    return logs

# Get wellness log for a specific date
@router.get("/{log_date}", response_model=WellnessLogResponse)
async def get_wellness_log_by_date(log_date: str, current_user: dict = Depends(get_current_user)):
    try:
        parsed_date = datetime.fromisoformat(log_date).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    log = await wellness_collection.find_one({"user_id": str(current_user["_id"]), "date": parsed_date.isoformat()})
    if not log:
        raise HTTPException(status_code=404, detail="No log found for this date")

    return WellnessLogResponse(
        id=str(log["_id"]),
        user_id=log["user_id"],
        sleep_hours=log["sleep_hours"],
        water_intake_liters=log["water_intake_liters"],
        steps=log["steps"],
        mood=log.get("mood"),
        date=datetime.fromisoformat(log["date"])
    )

# Update wellness log
@router.put("/{log_id}", response_model=WellnessLogResponse)
async def update_wellness_log(log_id: str, update_data: WellnessLogUpdate, current_user: dict = Depends(get_current_user)):
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    log = await wellness_collection.find_one_and_update(
        {"_id": ObjectId(log_id), "user_id": str(current_user["_id"])},
        {"$set": update_dict},
        return_document=True
    )

    if not log:
        raise HTTPException(status_code=404, detail="Wellness log not found")

    return WellnessLogResponse(
        id=str(log["_id"]),
        user_id=log["user_id"],
        sleep_hours=log["sleep_hours"],
        water_intake_liters=log["water_intake_liters"],
        steps=log["steps"],
        mood=log.get("mood"),
        date=datetime.fromisoformat(log["date"])
    )

# Delete wellness log
@router.delete("/{log_id}")
async def delete_wellness_log(log_id: str, current_user: dict = Depends(get_current_user)):
    result = await wellness_collection.delete_one({"_id": ObjectId(log_id), "user_id": str(current_user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Wellness log not found")

    return {"msg": "Wellness log deleted successfully"}