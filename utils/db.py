import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["kommuniti"]

# Collections - Core Collections
users_col = db["users"]
requests_col = db["service_requests"]
schedules_col = db["schedules"]
calendar_config_col = db["calendar_config"]

# Collections - Community Features
communities_col = db["communities"]
events_col = db["events"]
invitations_col = db["invitations"]


def initialize_db():
    """Set up database indexes and default data"""
    # Create indexes for better query performance
    users_col.create_index("telegram_id", unique=True)
    users_col.create_index("username", unique=True)
    requests_col.create_index("user_id")
    requests_col.create_index("status")

    # Community collections indexes
    communities_col.create_index("name", unique=True)
    events_col.create_index("date")
    events_col.create_index("organizer")
    invitations_col.create_index("event_id")
    invitations_col.create_index("recipient_id")

    # Ensure admin user exists
    if not users_col.find_one({"username": "admin"}):
        users_col.insert_one({
            "username": "admin",
            "password": "admin123",  # Should be hashed in production
            "role": "admin",
            "name": "Admin User"
        })

    # Ensure default community exists
    if not communities_col.find_one({"name": "Default"}):
        communities_col.insert_one({
            "name": "Default",
            "description": "Main community group",
            "members": ["admin"],
            "created_at": datetime.now()
        })

    print("Database initialized with community features")


if __name__ == "__main__":
    from datetime import datetime
    initialize_db()
    print("Total users:", users_col.count_documents({}))
    print("Total requests:", requests_col.count_documents({}))
    print("Total communities:", communities_col.count_documents({}))
    print("Total events:", events_col.count_documents({}))
    print("Total invitations:", invitations_col.count_documents({}))
