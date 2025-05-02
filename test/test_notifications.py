import sys
import os
import logging
from bson import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.notifications import send_notification, notify_assignment, notify_completion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_direct_notification():
    """Test sending a direct notification to a chat ID"""
    chat_id = input("Enter telegram chat ID to test: ")
    result = send_notification(
        chat_id,
        "🧪 *Test Notification*\n\nThis is a test message from KommunityKonect."
    )
    print(f"Notification sent: {result}")

def test_assignment_notification():
    """Test assignment notification"""
    # This requires valid data in your database
    request_id = input("Enter request ID: ")
    serviceman_username = input("Enter serviceman username: ")
    
    result = notify_assignment(request_id, serviceman_username)
    print(f"Assignment notification sent: {result}")

def test_completion_notification():
    """Test completion notification"""
    # This requires valid data in your database
    job_id = input("Enter job ID: ")
    serviceman_username = input("Enter serviceman username: ")
    
    result = notify_completion(job_id, serviceman_username)
    print(f"Completion notification sent: {result}")

if __name__ == "__main__":
    print("Notification Test Utility")
    print("1. Test direct notification")
    print("2. Test assignment notification")
    print("3. Test completion notification")
    
    choice = input("Select test (1-3): ")
    
    if choice == "1":
        test_direct_notification()
    elif choice == "2":
        test_assignment_notification()
    elif choice == "3":
        test_completion_notification()
    else:
        print("Invalid choice")
