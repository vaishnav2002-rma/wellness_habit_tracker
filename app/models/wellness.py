from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WellnessLogCreate(BaseModel):
    sleep_hours: float = Field(..., ge=0, le=24)
    water_intake_liters: float = Field(..., ge=0, le=10)
    steps: int = Field(..., ge=0)
    mood: Optional[str] = Field(None, max_length=50)

class WellnessLogUpdate(BaseModel):
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    water_intake_liters: Optional[float] = Field(None, ge=0, le=10)
    steps: Optional[int] = Field(None, ge=0)
    mood: Optional[str] = Field(None, max_length=50)

class WellnessLogResponse(BaseModel):
    id: str
    user_id: str
    sleep_hours: float
    water_intake_liters: float
    steps: int
    mood: Optional[str]
    date: datetime
