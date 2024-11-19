# app/utils.py
from datetime import datetime, timedelta
import pytz
from typing import List, Dict

def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """Convert datetime between timezones"""
    from_timezone = pytz.timezone(from_tz)
    to_timezone = pytz.timezone(to_tz)
    
    dt_with_tz = from_timezone.localize(dt)
    return dt_with_tz.astimezone(to_timezone)

def merge_time_slots(slots: List[tuple]) -> List[tuple]:
    """Merge overlapping time slots"""
    if not slots:
        return []
    
    # Sort slots by start time
    sorted_slots = sorted(slots, key=lambda x: x[0])
    merged = [sorted_slots[0]]
    
    for current in sorted_slots[1:]:
        previous = merged[-1]
        if current[0] <= previous[1]:
            merged[-1] = (previous[0], max(previous[1], current[1]))
        else:
            merged.append(current)
    
    return merged