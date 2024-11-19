# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import pytz
from . import models, schemas, utils
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/api/v1/availability", response_model=schemas.AvailabilityResponse)
def get_common_availability(
    request: schemas.AvailabilityRequest,
    db: Session = Depends(get_db)
):
    # Validate date range
    if request.end_date < request.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Initialize result dictionary
    result = {}
    
    # Process each date in the range
    current_date = request.start_date
    while current_date <= request.end_date:
        # Get day of week (0-6, Monday is 0)
        day_of_week = current_date.weekday()
        
        # Get all users' schedules for this day
        available_slots = []
        
        for user_id in request.user_ids:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            # Get weekly schedule
            weekly_schedule = db.query(models.WeeklySchedule).filter(
                models.WeeklySchedule.user_id == user_id,
                models.WeeklySchedule.day_of_week == day_of_week
            ).all()
            
            # Get specific schedule for this date
            specific_schedule = db.query(models.SpecificSchedule).filter(
                models.SpecificSchedule.user_id == user_id,
                models.SpecificSchedule.date == current_date
            ).all()
            
            # Get events for this date
            events = db.query(models.Event).filter(
                models.Event.user_id == user_id,
                models.Event.start_datetime >= datetime.combine(current_date, datetime.min.time()),
                models.Event.end_datetime < datetime.combine(current_date + timedelta(days=1), datetime.min.time())
            ).all()
            
            # Convert schedules to user's timezone
            day_slots = []
            
            # Process weekly schedule
            for schedule in weekly_schedule:
                start_dt = datetime.combine(current_date, schedule.start_time)
                end_dt = datetime.combine(current_date, schedule.end_time)
                start_dt = utils.convert_timezone(start_dt, user.timezone, request.timezone)
                end_dt = utils.convert_timezone(end_dt, user.timezone, request.timezone)
                day_slots.append((start_dt, end_dt))
            
            # Process specific schedule
            for schedule in specific_schedule:
                start_dt = datetime.combine(current_date, schedule.start_time)
                end_dt = datetime.combine(current_date, schedule.end_time)
                start_dt = utils.convert_timezone(start_dt, user.timezone, request.timezone)
                end_dt = utils.convert_timezone(end_dt, user.timezone, request.timezone)
                day_slots.append((start_dt, end_dt))
            
            # Remove event times from available slots
            final_slots = []
            for start_dt, end_dt in utils.merge_time_slots(day_slots):
                current_slot_start = start_dt
                for event in sorted(events, key=lambda x: x.start_datetime):
                    event_start = utils.convert_timezone(event.start_datetime, user.timezone, request.timezone)
                    event_end = utils.convert_timezone(event.end_datetime, user.timezone, request.timezone)
                    
                    if current_slot_start < event_start:
                        final_slots.append((current_slot_start, event_start))
                    current_slot_start = max(current_slot_start, event_end)
                
                if current_slot_start < end_dt:
                    final_slots.append((current_slot_start, end_dt))
            
            available_slots.append(final_slots)
        
        # Find common slots among all users
        common_slots = available_slots[0] if available_slots else []
        for user_slots in available_slots[1:]:
            new_common_slots = []
            for slot1 in common_slots:
                for slot2 in user_slots:
                    if slot1[0] < slot2[1] and slot2[0] < slot1[1]:
                        new_common_slots.append((
                            max(slot1[0], slot2[0]),
                            min(slot1[1], slot2[1])
                        ))
            common_slots = utils.merge_time_slots(new_common_slots)
        
        # Format slots for response
        if common_slots:
            formatted_slots = [
                f"{slot[0].strftime('%I:%M%p').lower()}-{slot[1].strftime('%I:%M%p').lower()}"
                for slot in common_slots
            ]
            result[current_date.strftime("%d-%m-%Y")] = formatted_slots
        
        current_date += timedelta(days=1)
    
    return {"dates": result}