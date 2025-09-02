from fastapi import APIRouter, Depends, HTTPException
from app.models.habit import HabitCreate, HabitResponse, HabitListResponse
from app.utils.security import get_current_user
from app.database import habits_collection
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/habits", tags=["Habits"])

habits_collection = habits_collection["habits"]

# ✅ Create a new habit
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

# ✅ Get all habits for logged-in user
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

# ✅ Get habit by ID
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
