from pydantic import BaseModel
from datetime import date, time, datetime
from typing import List, Optional

class TimeSlot(BaseModel):
    start_time: str
    end_time: str

class AvailabilityRequest(BaseModel):
    user_ids: List[int]
    start_date: date
    end_date: date
    timezone: str

class AvailabilityResponse(BaseModel):
    dates: dict[str, List[str]]