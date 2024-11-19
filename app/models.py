from sqlalchemy import Column, Integer, String, Time, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    timezone = Column(String, default="UTC")
    weekly_schedules = relationship("WeeklySchedule", back_populates="user")
    specific_schedules = relationship("SpecificSchedule", back_populates="user")
    events = relationship("Event", back_populates="user")

class WeeklySchedule(Base):
    __tablename__ = "weekly_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day_of_week = Column(Integer)  # 0-6 for Monday-Sunday
    start_time = Column(Time)
    end_time = Column(Time)
    user = relationship("User", back_populates="weekly_schedules")

class SpecificSchedule(Base):
    __tablename__ = "specific_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    user = relationship("User", back_populates="specific_schedules")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    user = relationship("User", back_populates="events")
