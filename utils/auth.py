import hashlib
import logging
from utils.db import users_col

def verify_user(username, password):
    """Verify user credentials"""
    # In production, passwords should be hashed
    user = users_col.find_one({"username": username})
    
    if not user:
        logging.warning(f"Login attempt: User {username} not found")
        return None
    
    # Simple password check (use proper hashing in production)
    if user.get("password") == password:
        logging.info(f"User {username} logged in successfully")
        return user
    else:
        logging.warning(f"Login attempt: Invalid password for {username}")
        return None

def register_user(username, password, role="user", name=None, telegram_id=None):
    """Register a new user"""
    # Check if username exists
    if users_col.find_one({"username": username}):
        return False, "Username already exists"
    
    # Create user document
    user_doc = {
        "username": username,
        "password": password,  # In production, use hashed passwords
        "role": role,
        "name": name or username
    }
    
    if telegram_id:
        user_doc["telegram_id"] = telegram_id
    
    users_col.insert_one(user_doc)
    return True, "User registered successfully"
