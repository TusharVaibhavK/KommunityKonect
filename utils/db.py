import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["kommuniti"]

# Collections
users_col = db["users"]
requests_col = db["service_requests"]

def initialize_db():
    """Set up database indexes and default data"""
    # Create indexes for better query performance
    users_col.create_index("telegram_id", unique=True)
    users_col.create_index("username", unique=True)
    requests_col.create_index("user_id")
    requests_col.create_index("status")
    
    # Ensure admin user exists
    if not users_col.find_one({"username": "admin"}):
        users_col.insert_one({
            "username": "admin",
            "password": "admin123",  # Should be hashed in production
            "role": "admin",
            "name": "Admin User"
        })
    
    print("Database initialized")

if __name__ == "__main__":
    initialize_db()
    print("Total users:", users_col.count_documents({}))
    print("Total requests:", requests_col.count_documents({}))
