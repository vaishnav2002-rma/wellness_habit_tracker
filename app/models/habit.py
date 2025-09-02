from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class HabitCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    frequency: str = Field(..., pattern="^(daily|weekly|monthly)$")

class HabitResponse(BaseModel):
    id: str
    user_id: str
    name: str
    frequency: str
    created_at: datetime

class HabitListResponse(BaseModel):
    habits: list[HabitResponse]
