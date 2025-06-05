"""
Database initialization script to properly setup collections and indexes
"""
from pymongo import MongoClient, ASCENDING
from pymongo.errors import OperationFailure

# Connect to MongoDB


def init_database(connection_string="mongodb://localhost:27017/"):
    client = MongoClient(connection_string)
    db = client["kommunity_konect"]

    # Initialize users collection with proper indexes
    users_col = db["users"]

    # Create indexes
    try:
        # Drop the existing telegram_id index that's causing issues
        users_col.drop_index("telegram_id_1")
        print("Dropped existing telegram_id index")
    except OperationFailure:
        print("No existing telegram_id index to drop")

    # Create a new index that allows for sparse values
    users_col.create_index([("telegram_id", ASCENDING)],
                           unique=True, sparse=True)
    users_col.create_index([("username", ASCENDING)], unique=True)

    print("Database initialized with proper indexes")
    return client


if __name__ == "__main__":
    client = init_database()
    print("Database initialization complete")
