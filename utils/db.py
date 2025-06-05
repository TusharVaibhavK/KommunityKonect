"""
Database connection module for KommunityKonect
Handles MongoDB connection and collections
"""
import os
import sys
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection string
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "kommunity_konect")

# Initialize connection and collections
client = None
db = None
requests_col = None
users_col = None
schedules_col = None
calendar_config_col = None


def connect_to_db():
    """Establish connection to MongoDB"""
    global client, db, requests_col, users_col, schedules_col, calendar_config_col

    if not MONGO_URI:
        logger.error("MONGO_URI environment variable is not set")
        sys.exit(
            "MongoDB connection string not found. Please set MONGO_URI environment variable.")

    try:
        # Create a MongoDB client with increased timeout
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

        # Verify connection works by pinging the server
        client.admin.command('ping')

        logger.info("Connected to MongoDB successfully")

        # Get database and collections
        db = client[DB_NAME]
        requests_col = db["service_requests"]
        users_col = db["users"]
        schedules_col = db["schedules"]
        calendar_config_col = db["calendar_config"]

        # Create indexes if they don't exist
        requests_col.create_index("user_id")
        requests_col.create_index("status")
        users_col.create_index("username", unique=True)
        users_col.create_index("telegram_id", unique=True)

        return True

    except ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        sys.exit(f"Database connection failed: {e}")

    except ConfigurationError as e:
        logger.error(f"MongoDB configuration error: {e}")
        sys.exit(f"Database configuration error: {e}")

    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        sys.exit(f"Unexpected database error: {e}")


# Connect to database on module load
connect_to_db()
