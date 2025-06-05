# Import statements (make sure they work when imported from project root)
import os
import sys
import requests
import time
import logging
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId

# Standard imports for this module that should work when called from project root
from utils.image_processing import analyze_telegram_photo
from utils.db import requests_col, users_col
from service_agents.serviceman_agent import run_agent
from utils.notifications import notify_assignment, notify_completion

# Initialize
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# State tracking
LAST_UPDATE_ID = 0
PROCESSED_MESSAGES = set()
USER_STATES = {}
# Store message IDs to prevent duplicates
SENT_MESSAGES = set()


def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    """Enhanced message sender with deduplication and error handling"""
    # Create a simple hash of the message to prevent duplicates
    message_hash = f"{chat_id}:{text[:20]}"
    if message_hash in SENT_MESSAGES:
        logging.debug(f"Skipping duplicate message: {message_hash}")
        return

    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json=payload,
            timeout=10
        )

        if response.ok:
            # Add to sent messages cache
            SENT_MESSAGES.add(message_hash)
            # Limit cache size to prevent memory issues
            if len(SENT_MESSAGES) > 1000:
                SENT_MESSAGES.clear()
        else:
            logging.error(f"Message failed to {chat_id}: {response.text}")
    except Exception as e:
        logging.error(f"send_message error: {str(e)}")


def is_serviceman(chat_id):
    """Check if user has serviceman role"""
    user = users_col.find_one({"telegram_id": str(chat_id)})
    return user and user.get("role") == "serviceman"


def get_serviceman_username(chat_id):
    """Fetch serviceman's internal username"""
    user = users_col.find_one({"telegram_id": str(chat_id)})
    return user.get("username") if user else None


def send_welcome(chat_id):
    """Updated welcome with role detection"""
    if is_serviceman(chat_id):
        buttons = [
            [{"text": "📋 My Jobs"}, {"text": "❓ Help"}]
        ]
    else:
        buttons = [
            [{"text": "📤 Submit Request"}],
            [{"text": "❓ Help"}]
        ]

    send_message(
        chat_id,
        "👋 *Welcome to CommunityConnect!*",
        reply_markup={
            "keyboard": buttons,
            "resize_keyboard": True
        }
    )


def handle_serviceman_command(chat_id, command):
    """Process serviceman job management"""
    username = get_serviceman_username(chat_id)
    if not username:
        send_message(chat_id, "⚠️ Your account isn't linked. Contact admin.")
        return

    try:
        # Check if command is for completion
        if command.startswith("/jobs complete ") or command.startswith("complete "):
            # Extract job_id from command
            parts = command.split()
            job_id = parts[-1]

            # Notify user about completion using the centralized notification module
            completion_success = notify_completion(job_id, username)
            if completion_success:
                send_message(
                    chat_id, f"✅ Job #{job_id[-6:]} marked as complete. User has been notified.")
            else:
                send_message(
                    chat_id, f"⚠️ Failed to update job or notify user. Please try again.")
            return

        # Check if command is for assignment
        if command.startswith("/assign ") or command.startswith("assign "):
            # Extract job_id from command
            parts = command.split()
            job_id = parts[-1]

            # Notify user about assignment using the centralized notification module
            assignment_success = notify_assignment(job_id, username)
            if assignment_success:
                send_message(
                    chat_id, f"✅ Job #{job_id[-6:]} assigned to you. User has been notified.")
            else:
                send_message(
                    chat_id, f"⚠️ Failed to update job or notify user. Please try again.")
            return

        response = run_agent(command, serviceman_username=username)
        send_message(chat_id, response)
    except Exception as e:
        logging.error(f"Agent error: {str(e)}")
        send_message(chat_id, "🔧 System busy. Try again later.")


def send_help(chat_id):
    """Send help information"""
    help_text = (
        "*📱 How to use this bot:*\n\n"
        "• Use *📤 Submit Request* to report a service issue\n"
        "• Follow the prompts to provide details\n"
        "• Our team will review and assign a specialist\n"
        "• You'll receive notifications about your request\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/submit - Submit a new request\n"
        "/status - Check request status"
    )
    send_message(chat_id, help_text)


def start_request_flow(chat_id):
    """Start the request submission flow"""
    USER_STATES[chat_id] = "AWAITING_CATEGORY"

    # Create keyboard with service categories
    categories = ["Plumbing", "Electrical", "Carpentry",
                  "Appliance Repair", "Painting", "Other"]
    buttons = [[{"text": cat}] for cat in categories]
    buttons.append([{"text": "❌ Cancel"}])

    send_message(
        chat_id,
        "Please select a service category:",
        reply_markup={
            "keyboard": buttons,
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
    )


def handle_category_selection(chat_id, category):
    """Process category selection"""
    if category == "❌ Cancel":
        USER_STATES.pop(chat_id, None)
        send_welcome(chat_id)
        return

    # Store category in temporary state
    if chat_id not in USER_STATES:
        USER_STATES[chat_id] = {}
    USER_STATES[chat_id] = {
        "state": "AWAITING_DESCRIPTION", "category": category}

    send_message(
        chat_id,
        f"Category selected: *{category}*\n\nPlease describe the issue in detail:",
        {"remove_keyboard": True}
    )


def handle_description(chat_id, description):
    """Process description input"""
    USER_STATES[chat_id]["description"] = description
    USER_STATES[chat_id]["state"] = "AWAITING_LOCATION"

    send_message(
        chat_id,
        "Thank you! Now, please provide the location (e.g., apartment number, address):"
    )


def handle_location(chat_id, location):
    """Process location input"""
    USER_STATES[chat_id]["location"] = location
    USER_STATES[chat_id]["state"] = "AWAITING_PHOTO"

    send_message(
        chat_id,
        "Almost done! Please send a photo of the issue (or type 'skip' to continue without a photo):"
    )


def handle_photo(chat_id, photo_file_id=None):
    """Process photo submission or skip"""
    request_data = USER_STATES.get(chat_id, {})

    if photo_file_id:
        # Get photo URL
        file_path_response = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getFile",
            params={"file_id": photo_file_id}
        ).json()

        if file_path_response["ok"]:
            file_path = file_path_response["result"]["file_path"]
            photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
            request_data["photo_url"] = photo_url

            # Send processing message to user
            send_message(chat_id, "🔍 Analyzing your photo...")

            # Analyze photo with CLIP model
            try:
                analysis_result = analyze_telegram_photo(photo_url)

                # Log the analysis for debugging
                logging.info(f"Analysis result: {analysis_result}")

                # Store the full analysis result in the request data
                request_data["photo_analysis"] = analysis_result

                if analysis_result.get("success", False):
                    # Format the response for the user
                    issue_type = analysis_result.get(
                        "issue_type", "unknown issue")
                    confidence = analysis_result.get("confidence", 0)

                    # Create a user-friendly message
                    analysis_message = (
                        f"*📋 Issue Analysis:*\n\n"
                        f"• *Detected Problem:* {issue_type.replace('_', ' ').title()}\n"
                        f"• *Confidence:* {confidence:.1f}%\n\n"
                        f"Based on the image analysis, this appears to be a {issue_type.split()[0]} issue. "
                        f"Our service specialist will address this when assigned to your request."
                    )

                    send_message(chat_id, analysis_message)
                else:
                    # Handle error case
                    error_msg = analysis_result.get("error", "Unknown error")
                    logging.error(f"Photo analysis error: {error_msg}")
                    send_message(
                        chat_id,
                        "⚠️ I couldn't clearly identify the issue in your photo, but your request has been submitted and a specialist will review it."
                    )

            except Exception as e:
                logging.error(f"Photo analysis error: {str(e)}", exc_info=True)
                send_message(
                    chat_id,
                    "❗ There was an issue analyzing your photo, but your request has been recorded."
                )

    # Save request to database
    request_data.update({
        "user_id": str(chat_id),
        "status": "Pending",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Remove state field before saving
    if "state" in request_data:
        del request_data["state"]

    # Insert into database - handle potential duplicate key
    try:
        result = requests_col.insert_one(request_data)
        request_id = result.inserted_id
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        # Generate a new ObjectId and try again
        from bson.objectid import ObjectId
        request_data["_id"] = ObjectId()
        result = requests_col.insert_one(request_data)
        request_id = result.inserted_id

    # Clear user state
    USER_STATES.pop(chat_id, None)

    # Send confirmation
    send_message(
        chat_id,
        f"✅ *Request #{str(request_id)[-6:]} submitted successfully!*\n\n"
        f"• Category: {request_data.get('category', 'Not specified')}\n"
        f"• Status: Pending\n\n"
        "We'll notify you when a specialist is assigned."
    )

    # Return to main menu
    send_welcome(chat_id)

    # Save request to database with a new ObjectId
    request_data.update({
        "user_id": str(chat_id),
        "status": "Pending",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Remove state field before saving
    if "state" in request_data:
        del request_data["state"]

    # Insert into database - don't reuse IDs
    try:
        result = requests_col.insert_one(request_data)
        request_id = result.inserted_id
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        # Generate a new ObjectId and try again
        from bson.objectid import ObjectId
        request_data["_id"] = ObjectId()
        result = requests_col.insert_one(request_data)
        request_id = result.inserted_id

    # Clear user state
    USER_STATES.pop(chat_id, None)

    # Send confirmation
    send_message(
        chat_id,
        f"✅ *Request #{str(request_id)[-6:]} submitted successfully!*\n\n"
        f"• Category: {request_data.get('category', 'Not specified')}\n"
        f"• Status: Pending\n\n"
        "We'll notify you when a specialist is assigned."
    )

    # Return to main menu
    send_welcome(chat_id)


def send_long_message(chat_id, text, max_length=3900):
    """Split and send long messages to avoid Telegram's message length limit."""
    if len(text) <= max_length:
        return send_message(chat_id, text)

    parts = []
    for i in range(0, len(text), max_length):
        parts.append(text[i:i+max_length])

    for i, part in enumerate(parts):
        header = f"*Message ({i+1}/{len(parts)})*\n\n" if len(parts) > 1 else ""
        send_message(chat_id, header + part)


def process_message(chat_id, text, message):
    """Process incoming messages based on user state"""
    user_state = USER_STATES.get(chat_id, {})
    state = user_state.get("state") if isinstance(
        user_state, dict) else user_state

    # Command handling
    if text.startswith('/'):
        # Handle commands regardless of state
        if text == '/start':
            USER_STATES.pop(chat_id, None)  # Reset state
            send_welcome(chat_id)
            return
        elif text == '/status':
            show_current_requests(chat_id)
            return
        elif text == '/submit':
            start_request_flow(chat_id)
            return

    # State-based processing
    if state == "AWAITING_USERNAME":
        # Remove this state or implement handle_username function
        send_message(chat_id, "Username processing is not implemented yet.")
        USER_STATES.pop(chat_id, None)  # Reset the state
        send_welcome(chat_id)
    elif state == "AWAITING_CATEGORY":
        handle_category_selection(chat_id, text)
    elif state == "AWAITING_DESCRIPTION":
        handle_description(chat_id, text)
    elif state == "AWAITING_LOCATION":
        handle_location(chat_id, text)
    elif state == "AWAITING_PHOTO":
        if text and text.lower() == "skip":
            handle_photo(chat_id)  # Skip photo
        elif message.get("photo"):
            # Get the largest photo (last in array)
            photo = message["photo"][-1]
            handle_photo(chat_id, photo["file_id"])
        else:
            send_message(chat_id, "Please send a photo or type 'skip'.")
    else:
        # Default handling for messages
        if text == '📤 Submit Request':
            start_request_flow(chat_id)
        elif text == '❓ Help':
            send_help(chat_id)
        elif is_serviceman(chat_id):
            # Let serviceman agent handle unknown inputs
            response = run_agent(text, get_serviceman_username(chat_id))
            send_message(chat_id, response)


def handle_updates():
    global LAST_UPDATE_ID, PROCESSED_MESSAGES

    try:
        updates = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getUpdates",
            params={"offset": LAST_UPDATE_ID + 1,
                    "timeout": 30},  # Use long polling
            timeout=35
        ).json()

        for update in updates.get('result', []):
            LAST_UPDATE_ID = update['update_id']

            # Skip processed messages
            message = update.get('message', {})
            if not message:
                continue

            message_id = message.get('message_id')
            if not message_id or message_id in PROCESSED_MESSAGES:
                logging.debug(
                    f"Skipping already processed message: {message_id}")
                continue

            # Mark as processed immediately to prevent duplicate handling
            PROCESSED_MESSAGES.add(message_id)

            # Limit cache size
            if len(PROCESSED_MESSAGES) > 1000:
                PROCESSED_MESSAGES = set(list(PROCESSED_MESSAGES)[-500:])

            chat_id = message['chat']['id']
            text = message.get('text', '')

            # Process the message based on state
            process_message(chat_id, text, message)

            # Handle callbacks (button clicks)
            if 'callback_query' in update:
                handle_callback(update)

    except Exception as e:
        logging.error(f"Update loop failed: {str(e)}")


def handle_callback(update):
    """Process button clicks"""
    query = update["callback_query"]
    chat_id = query["message"]["chat"]["id"]

    if query["data"] == "check_status":
        show_current_requests(chat_id)

    # Acknowledge button press
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
        json={"callback_query_id": query["id"]}
    )


def show_current_requests(chat_id):
    """Display all requests with status"""
    requests = list(requests_col.find({
        "user_id": str(chat_id)
    }).sort("timestamp", -1))

    if not requests:
        send_message(chat_id, "You have no requests in the system.")
        return

    active_requests = [r for r in requests if r.get("status") != "Completed"]
    completed_requests = [
        r for r in requests if r.get("status") == "Completed"]

    if not active_requests and not completed_requests:
        send_message(chat_id, "You have no requests in the system.")
        return

    # Show active requests first
    if active_requests:
        send_message(chat_id, "📋 *Your Active Requests:*")
        for req in active_requests:
            status_icon = "🟡" if req["status"] == "Pending" else "🟢"
            message = (
                f"{status_icon} *Request #{str(req['_id'])[-6:]}*\n"
                f"• *Category*: {req.get('category', 'N/A')}\n"
                f"• *Status*: {req.get('status', 'Pending')}\n"
                f"• *Submitted*: {req.get('timestamp', 'N/A')}"
            )

            if req.get("assigned_to"):
                serviceman = users_col.find_one(
                    {"username": req["assigned_to"]})
                if serviceman:
                    message += f"\n• *Specialist*: {serviceman.get('name', '')} (@{serviceman.get('telegram', '')})"

            send_message(chat_id, message)

    # Show recently completed requests (limited to 3)
    if completed_requests:
        send_message(chat_id, "✅ *Recently Completed Requests:*")
        for req in completed_requests[:3]:  # Limit to 3 most recent
            message = (
                f"✓ *Request #{str(req['_id'])[-6:]}*\n"
                f"• *Category*: {req.get('category', 'N/A')}\n"
                f"• *Completed*: {req.get('completion_time', req.get('timestamp', 'N/A'))}"
            )
            send_message(chat_id, message)

        if len(completed_requests) > 3:
            send_message(
                chat_id, f"_...and {len(completed_requests) - 3} more completed requests_")

    # Return to main menu
    buttons = [
        [{"text": "📤 Submit Request"}],
        [{"text": "❓ Help"}]
    ]

    send_message(
        chat_id,
        "What would you like to do next?",
        reply_markup={
            "keyboard": buttons,
            "resize_keyboard": True
        }
    )
