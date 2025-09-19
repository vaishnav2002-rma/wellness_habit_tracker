from fastapi import APIRouter, Depends, HTTPException
from app.models.habit import HabitCreate, HabitUpdate,HabitResponse, HabitListResponse, HabitLogResponse
from app.utils.security import get_current_user
from app.database import habits_collection, habit_logs_collection
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/habits", tags=["Habits"])

# Create a new habit
@router.post("/", response_model=HabitResponse)
async def create_habit(habit: HabitCreate, current_user: dict = Depends(get_current_user)):
    new_habit = {
        "user_id": str(current_user["_id"]),
        "name": habit.name,      
        "frequency": habit.frequency,
        "created_at": datetime.utcnow()
    }
    result = await habits_collection.insert_one(new_habit)
    return HabitResponse(
        id=str(result.inserted_id),
        user_id=new_habit["user_id"],
        name=new_habit["name"],
        frequency=new_habit["frequency"],
        created_at=new_habit["created_at"]
    )

# Get all habits for logged-in user
@router.get("/", response_model=HabitListResponse)
async def get_habits(current_user: dict = Depends(get_current_user)):
    cursor = habits_collection.find({"user_id": str(current_user["_id"])})
    habits = []
    async for doc in cursor:
        habits.append(HabitResponse(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            name=doc["name"],
            frequency=doc["frequency"],
            created_at=doc["created_at"]
        ))
    return HabitListResponse(habits=habits)

# Get habit by ID
@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(habit_id: str, current_user: dict = Depends(get_current_user)):
    habit = await habits_collection.find_one({"_id": ObjectId(habit_id), "user_id": str(current_user["_id"])})
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return HabitResponse(
        id=str(habit["_id"]),
        user_id=habit["user_id"],
        name=habit["name"],
        frequency=habit["frequency"],
        created_at=habit["created_at"]
    )

# Update a habit
@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(habit_id: str, update_data: HabitUpdate, current_user: dict = Depends(get_current_user)):
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    habit = await habits_collection.find_one_and_update(
        {"_id": ObjectId(habit_id), "user_id": str(current_user["_id"])},
        {"$set": update_dict},
        return_document=True
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    return HabitResponse(
        id=str(habit["_id"]),
        user_id=habit["user_id"],
        name=habit["name"],
        frequency=habit["frequency"],
        created_at=habit["created_at"]
    )

# Delete a habit
@router.delete("/{habit_id}")
async def delete_habit(habit_id: str, current_user: dict = Depends(get_current_user)):
    result = await habits_collection.delete_one({"_id": ObjectId(habit_id), "user_id": str(current_user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"msg": "Habit deleted successfully"}

# Log habit completion for today
@router.post("/{habit_id}/log", response_model=HabitLogResponse)
async def log_habit_completion(habit_id: str, current_user: dict = Depends(get_current_user)):
    habit = await habits_collection.find_one({"_id": ObjectId(habit_id), "user_id": str(current_user["_id"])})
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    today = datetime.utcnow().date()
    existing_log = await habit_logs_collection.find_one({
        "habit_id": habit_id,
        "user_id": str(current_user["_id"]),
        "date": today.isoformat()
    })

    if existing_log:
        raise HTTPException(status_code=400, detail="Habit already logged for today")

    log_entry = {
        "habit_id": habit_id,
        "user_id": str(current_user["_id"]),
        "date": today.isoformat(),
        "status": "completed"       
    }
    await habit_logs_collection.insert_one(log_entry)

    return HabitLogResponse(
        habit_id=habit_id,
        user_id=str(current_user["_id"]),
        date=today,
        status="completed"
    )