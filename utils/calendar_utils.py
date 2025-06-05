from datetime import datetime, timedelta
from bson import ObjectId
from utils.db import schedules_col, calendar_config_col


def get_available_slots(serviceman, date):
    """
    Get available time slots for a serviceman on a specific date

    Args:
        serviceman: username of the serviceman
        date: datetime object for the day to check

    Returns:
        Dictionary with serviceman's schedule including available slots
    """
    # Format date to string for querying
    date_str = date.strftime("%Y-%m-%d")

    # Find schedule for the serviceman on the given date
    schedule = schedules_col.find_one({
        "serviceman": serviceman,
        "date": date_str
    })

    if not schedule:
        return {"serviceman": serviceman, "date": date_str, "time_slots": []}

    return schedule


def book_slot(request_id, serviceman, date, slot):
    """
    Book a time slot for a service request

    Args:
        request_id: ID of the service request
        serviceman: username of the serviceman
        date: datetime object for the day
        slot: dictionary with start and end times

    Returns:
        True if booking successful, False otherwise
    """
    date_str = date.strftime("%Y-%m-%d")

    # Find the schedule
    result = schedules_col.update_one(
        {
            "serviceman": serviceman,
            "date": date_str,
            "time_slots": {
                "$elemMatch": {
                    "start": slot["start"],
                    "end": slot["end"],
                    "booked_by": {"$exists": False}
                }
            }
        },
        {
            "$set": {
                "time_slots.$.booked_by": request_id
            }
        }
    )

    return result.modified_count > 0


def add_time_slot(serviceman, date, start_time, end_time):
    """
    Add a time slot to a serviceman's schedule

    Args:
        serviceman: username of the serviceman
        date: datetime object for the day
        start_time: start time string in format "HH:MM"
        end_time: end time string in format "HH:MM"

    Returns:
        True if slot added successfully, False otherwise
    """
    date_str = date.strftime("%Y-%m-%d")

    # Check if schedule exists for this day
    schedule = schedules_col.find_one({
        "serviceman": serviceman,
        "date": date_str
    })

    new_slot = {
        "start": start_time,
        "end": end_time
    }

    if schedule:
        # Add the slot to existing schedule
        result = schedules_col.update_one(
            {"serviceman": serviceman, "date": date_str},
            {"$push": {"time_slots": new_slot}}
        )
        return result.modified_count > 0
    else:
        # Create new schedule with this slot
        result = schedules_col.insert_one({
            "serviceman": serviceman,
            "date": date_str,
            "time_slots": [new_slot]
        })
        return result.inserted_id is not None
