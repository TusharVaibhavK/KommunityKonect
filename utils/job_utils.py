from datetime import datetime
from utils.db import requests_col

def log_job_action(job_id: str, action: str, by_user: str):
    """Track job state changes"""
    requests_col.update_one(
        {"_id": job_id},
        {"$push": {"logs": {
            "action": action,
            "by": by_user,
            "timestamp": datetime.utcnow()
        }}}
    )

def get_serviceman_jobs(username: str):
    """Fetch jobs with optional filtering"""
    return list(requests_col.find({
        "assigned_to": username,
        "status": {"$ne": "Completed"}
    }).sort("urgency", -1))