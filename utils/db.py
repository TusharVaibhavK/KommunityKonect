import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)

db = client["kommuniti"]
requests_col = db["service_requests"]
users_col = db["users"]
