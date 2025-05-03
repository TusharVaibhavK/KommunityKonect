from datetime import datetime, timedelta
from pymongo import MongoClient
from utils.db import schedules_col, calendar_config_col
from bson import ObjectId

def init_serviceman_schedule(serviceman_username: str, date: datetime):
    """Ensure a schedule document exists for a serviceman on a given date"""
    existing = schedules_col.find_one({
        "serviceman_id": serviceman_username,
        "date": date
    })
    if not existing:
        schedules_col.insert_one({
            "serviceman_id": serviceman_username,
            "date": date,
            "time_slots": [],
            "created_at": datetime.utcnow()
        })

def add_time_slot(serviceman_username: str, date: datetime, start: str, end: str):
    """Add available time slot (format HH:MM)"""
    schedules_col.update_one(
        {"serviceman_id": serviceman_username, "date": date},
        {"$push": {"time_slots": {
            "start": start,
            "end": end,
            "booked_by": None
        }}},
        upsert=True
    )

def get_available_slots(serviceman_username: str, date: datetime):
    """Return all slots for a serviceman on a date"""
    return schedules_col.find_one({
        "serviceman_id": serviceman_username,
        "date": date
    }) or {"time_slots": []}

def book_slot(request_id: str, serviceman_username: str, date: datetime, slot: dict):
    """Mark a time slot as booked"""
    schedules_col.update_one(
        {"serviceman_id": serviceman_username, "date": date},
        {"$set": {"time_slots.$[elem].booked_by": ObjectId(request_id)}},
        array_filters=[{"elem.start": slot["start"], "elem.booked_by": None}]
    )