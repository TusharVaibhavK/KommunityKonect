import os
import requests
import logging
from datetime import datetime
from bson import ObjectId
from utils.db import requests_col, users_col

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load Telegram token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_telegram_message(chat_id, text, parse_mode="Markdown"):
    """Send a message to a Telegram user"""
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            },
            timeout=10
        )
        
        if not response.ok:
            logger.error(f"Failed to send message: {response.text}")
            return False
        return True
    except Exception as e:
        logger.error(f"Telegram message error: {str(e)}")
        return False

def notify_assignment(request_id, serviceman_username):
    """
    Notify user that a serviceman has been assigned to their request
    
    Args:
        request_id (str): The ID of the request
        serviceman_username (str): Username of the assigned serviceman
        
    Returns:
        bool: Success or failure
    """
    try:
        # Convert string ID to ObjectId if needed
        if isinstance(request_id, str):
            request_id = ObjectId(request_id)
            
        # Get request details
        request = requests_col.find_one({"_id": request_id})
        if not request:
            logger.error(f"Request {request_id} not found for assignment notification")
            return False
            
        # Get user details
        user_id = request.get("user_id")
        if not user_id:
            logger.error(f"No user_id found for request {request_id}")
            return False
            
        # Get serviceman details
        serviceman = users_col.find_one({"username": serviceman_username})
        if not serviceman:
            logger.error(f"Serviceman {serviceman_username} not found")
            return False
            
        # Update request status in database
        result = requests_col.update_one(
            {"_id": request_id},
            {
                "$set": {
                    "status": "Assigned",
                    "assigned_to": serviceman_username,
                    "assignment_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        )
        
        if not result.modified_count:
            logger.warning(f"Failed to update request {request_id} status")
            
        # Prepare notification message
        message = (
            f"🔔 *Service Update: Request #{str(request_id)[-6:]}*\n\n"
            f"Good news! A specialist has been assigned to your {request.get('category', 'service')} request.\n\n"
            f"*Specialist:* {serviceman.get('name', 'Your specialist')}\n"
            f"*Contact:* @{serviceman.get('telegram', '')}\n\n"
            f"They will be in touch shortly to address your issue at {request.get('location', 'your location')}."
        )
        
        # Send notification to user
        success = send_telegram_message(user_id, message)
        return success
        
    except Exception as e:
        logger.error(f"Assignment notification error: {str(e)}")
        return False

def notify_completion(request_id, serviceman_username):
    """
    Notify user that their request has been completed
    
    Args:
        request_id (str): The ID of the request
        serviceman_username (str): Username of the serviceman who completed the job
        
    Returns:
        bool: Success or failure
    """
    try:
        # Convert string ID to ObjectId if needed
        if isinstance(request_id, str):
            request_id = ObjectId(request_id)
            
        # Get request details
        request = requests_col.find_one({"_id": request_id})
        if not request:
            logger.error(f"Request {request_id} not found for completion notification")
            return False
            
        # Verify the serviceman is assigned to this request
        if request.get("assigned_to") != serviceman_username:
            logger.warning(f"Serviceman {serviceman_username} not assigned to request {request_id}")
            # Continue anyway - may be a supervisor or admin override
            
        # Get user details
        user_id = request.get("user_id")
        if not user_id:
            logger.error(f"No user_id found for request {request_id}")
            return False
            
        # Update request status in database
        completion_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        result = requests_col.update_one(
            {"_id": request_id},
            {
                "$set": {
                    "status": "Completed",
                    "completed_by": serviceman_username,
                    "completion_time": completion_time
                }
            }
        )
        
        if not result.modified_count:
            logger.warning(f"Failed to update request {request_id} status to Completed")
            
        # Prepare notification message
        message = (
            f"✅ *Service Completed: Request #{str(request_id)[-6:]}*\n\n"
            f"Your {request.get('category', 'service')} request has been marked as completed.\n\n"
            f"*Location:* {request.get('location', 'Not specified')}\n"
            f"*Completed on:* {completion_time}\n\n"
            f"Thank you for using our service! If you have any feedback or the issue wasn't fully resolved, please let us know."
        )
        
        # Send notification to user
        success = send_telegram_message(user_id, message)
        return success
        
    except Exception as e:
        logger.error(f"Completion notification error: {str(e)}")
        return False