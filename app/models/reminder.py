from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ReminderCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    reminder_type: str = Field(..., pattern="^(habit|wellness)$")  # habit or wellness
    target_id: Optional[str] = None  # e.g. habit_id or wellness_log_id
    reminder_time: datetime  # ISO format datetime (with or without timezone)
    repeat: Optional[str] = Field(None, pattern="^(daily|weekly|none)$")  # repetition rule

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Drink Water",
                "reminder_type": "habit",
                "target_id": "64fa12345",
                "reminder_time": "2025-10-21T15:30:00",
                "repeat": "none"
            }
        }
    )


class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    reminder_time: Optional[datetime] = None
    repeat: Optional[str] = Field(None, pattern="^(daily|weekly|none)$")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Morning Jog",
                "reminder_time": "2025-10-22T07:00:00",
                "repeat": "daily"
            }
        }
    )


class ReminderResponse(BaseModel):
    id: str
    user_id: str
    title: str
    reminder_type: str
    target_id: Optional[str] = None
    reminder_time: datetime
    repeat: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "68bac9221fe6a8747ded5235",
                "user_id": "68b67cb62345c22e0e1b4b5e",
                "title": "Drink Water",
                "reminder_type": "habit",
                "target_id": "64fa12345",
                "reminder_time": "2025-10-21T15:30:00",
                "repeat": "none",
                "created_at": "2025-10-21T11:27:30"
            }
        }
    )
