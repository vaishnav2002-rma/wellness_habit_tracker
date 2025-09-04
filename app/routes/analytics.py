from fastapi import APIRouter, Depends, HTTPException
from app.utils.security import get_current_user
from app.database import db
from datetime import datetime, timedelta
from app.utils.mongo_helpers import serialize_doc

router = APIRouter(prefix="/analytics", tags=["Analytics"])

habits_collection = db["habits"]
habit_logs_collection = db["habit_logs"]
wellness_collection = db["wellness_logs"]

# 1. Habit Consistency Report
@router.get("/habits")
async def habit_consistency(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    habits = await habits_collection.find({"user_id": user_id}).to_list(None)

    report = []
    for habit in habits:
        total_days = 30  # last 30 days
        start_date = datetime.utcnow().date() - timedelta(days=30)
        logs = await habit_logs_collection.find({
            "habit_id": str(habit["_id"]),
            "user_id": user_id,
            "date": {"$gte": start_date.isoformat()}
        }).to_list(None)

        completed_days = len(logs)
        consistency = (completed_days / total_days) * 100 if total_days else 0

        report.append({
            "habit_name": habit["name"],
            "frequency": habit["frequency"],
            "completed_days": completed_days,
            "consistency_percent": round(consistency, 2)
        })

    return {"habit_consistency": report}


# 2. Wellness Trends (last 30 days)
@router.get("/wellness")
async def wellness_trends(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    start_date = datetime.utcnow().date() - timedelta(days=30)

    cursor = wellness_collection.find({
        "user_id": user_id,
        "date": {"$gte": start_date.isoformat()}
    })

    sleep = []
    steps = []
    water = []
    moods = []

    async for log in cursor:
        sleep.append(log["sleep_hours"])
        steps.append(log["steps"])
        water.append(log["water_intake_liters"])
        if log.get("mood"):
            moods.append(log["mood"])

    return {
        "average_sleep": round(sum(sleep)/len(sleep), 2) if sleep else 0,
        "average_steps": round(sum(steps)/len(steps), 2) if steps else 0,
        "average_water_intake": round(sum(water)/len(water), 2) if water else 0,
        "mood_trend": moods[-7:] if moods else []  # last 7 mood entries
    }


# 3. Overall Progress Summary
@router.get("/summary")
async def progress_summary(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    today = datetime.utcnow().date()

    # Count total habits
    total_habits = await habits_collection.count_documents({"user_id": user_id})

    # Today’s habit logs
    today_habits = await habit_logs_collection.count_documents({"user_id": user_id, "date": today.isoformat()})

    # Today’s wellness log
    wellness_today = await wellness_collection.find_one({"user_id": user_id, "date": today.isoformat()})

    summary = {
        "total_habits": total_habits,
        "habits_completed_today": today_habits,
        "wellness_today": serialize_doc(wellness_today) if wellness_today else "No log yet"
    }

    return summary
