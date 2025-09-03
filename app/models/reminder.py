from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReminderCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    reminder_type: str = Field(..., pattern="^(habit|wellness)$")  # habit or wellness
    target_id: Optional[str] = None  # e.g. habit_id or wellness_log_id
    reminder_time: datetime
    repeat: Optional[str] = Field(None, pattern="^(daily|weekly|none)$")  # repetition rule

class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    reminder_time: Optional[datetime] = None
    repeat: Optional[str] = Field(None, pattern="^(daily|weekly|none)$")

class ReminderResponse(BaseModel):
    id: str
    user_id: str
    title: str
    reminder_type: str
    target_id: Optional[str]
    reminder_time: datetime
    repeat: Optional[str]
    created_at: datetime
