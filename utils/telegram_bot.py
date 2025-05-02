import requests
import os
import time
from dotenv import load_dotenv
from utils.image_processing import analyze_telegram_photo 
from utils.db import requests_col  # Your existing collection
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Persistent tracking
LAST_UPDATE_ID = 0
PROCESSED_MESSAGES = set()

def send_welcome(chat_id):
    """Send welcome message with photo button"""
    keyboard = {
        "keyboard": [
            [{"text": "📤 Send Photo"}],
            [{"text": "❓ Help"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": (
                "🚀 *Welcome to ServiceBot!*\n\n"
                "1. Tap 📤 Send Photo to share your issue\n"
                "2. Add a brief description\n"
                "3. We'll connect you with a specialist"
            ),
            "reply_markup": keyboard,
            "parse_mode": "Markdown"
        }
    )

def handle_photo(chat_id, file_id):
    """Process received photos with analysis"""
    # Get file path (existing code)
    file_info = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}"
    ).json()
    file_path = file_info['result']['file_path']
    photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    
    # Analyze image (existing code)
    analysis = analyze_telegram_photo(photo_url)
    
    if analysis.get("success"):
        # Save to MongoDB - MATCHING YOUR STREAMLIT UI STRUCTURE
        new_request = {
            "user_id": str(chat_id),
            "name": "Telegram User",  # Default since name isn't collected
            "category": analysis["issue_type"],
            "description": "Submitted via Telegram",
            "location": "Not specified",
            "urgency": "Medium",
            "status": "Pending",
            "photo_url": photo_url,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "telegram"  # Helpful for filtering
        }
        requests_col.insert_one(new_request)
        
        response_text = (
            f"📋 *Request Received*\n\n"
            f"• **Issue Type**: {analysis['issue_type']}\n"
            f"• **Confidence**: {analysis['confidence']:.1f}%\n\n"
            f"Our admin will assign a specialist shortly."
        )
    else:
        response_text = f"⚠️ Analysis failed: {analysis.get('error')}"
    
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": response_text,
            "reply_markup": {"remove_keyboard": True}
        }
    )
    
    print(f"Request saved for {chat_id}: {analysis['issue_type']}")

def handle_updates():
    global LAST_UPDATE_ID, PROCESSED_MESSAGES
    
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={LAST_UPDATE_ID + 1}"
        response = requests.get(url, timeout=15).json()
        
        if not response.get('result'):
            return

        for update in response['result']:
            message = update.get('message', {})
            message_id = message.get('message_id')
            
            if not message_id or message_id in PROCESSED_MESSAGES:
                continue
                
            PROCESSED_MESSAGES.add(message_id)
            LAST_UPDATE_ID = update['update_id']
            
            chat_id = message['chat']['id']
            text = message.get('text', '')

            # Handle commands
            if text in ['/start', '❓ Help']:
                send_welcome(chat_id)
                print(f"Sent welcome to {chat_id}")
            
            # Handle photos
            elif 'photo' in message:
                handle_photo(chat_id, message['photo'][-1]['file_id'])  # Get highest resolution

    except Exception as e:
        print(f"Error: {str(e)}")

def notify_assignment(request_id, serviceman_username):
    """Notify both user and serviceman about assignment"""
    request = requests_col.find_one({"_id": request_id})
    
    # Notify user who submitted request
    if request.get('source') == 'telegram':
        send_message(
            request['user_id'],
            f"👷 *Specialist Assigned*\n\n"
            f"Request #{request_id}\n"
            f"Category: {request['category']}\n"
            f"Serviceman: @{serviceman_username}\n\n"
            f"Status: {request['status']}"
        )
    
    # Notify serviceman (if they have Telegram ID in your system)
    serviceman = db.users.find_one({"username": serviceman_username})
    if serviceman and 'telegram' in serviceman:
        send_message(
            serviceman['telegram'],
            f"🔧 *New Assignment*\n\n"
            f"Request #{request_id}\n"
            f"Category: {request['category']}\n"
            f"Location: {request['location']}\n\n"
            f"Photo: {request['photo_url']}"
        )

if __name__ == "__main__":
    print("ServiceBot ready (Photo handling enabled)")
    while True:
        handle_updates()
        time.sleep(0.5)