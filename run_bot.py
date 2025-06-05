"""
Bot runner script - Run this from the project root directory
to start the Telegram bot without import errors
"""
import os
import sys
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_debug.log'),
        logging.StreamHandler()  # Print to console
    ]
)
logger = logging.getLogger(__name__)


def check_environment():
    """Check that all required environment variables are set"""
    required_vars = ["TELEGRAM_BOT_TOKEN", "MONGODB_URI"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        logger.error(
            f"Missing required environment variables: {', '.join(missing)}")
        return False
    return True


def main():
    """Main function to run the bot"""
    try:
        print("Starting KommunityKonect ServiceBot...")

        # Check environment variables
        if not check_environment():
            return 1

        # Ensure database connection works
        from utils.db import connect_to_db
        if not connect_to_db():
            logger.error("Failed to connect to database")
            return 1

        # Import the bot module after database is confirmed working
        from utils.telegram_bot import handle_updates

        print("KommunityKonect ServiceBot is running...")
        logger.info("Bot started successfully")

        # Run the bot's update loop
        while True:
            handle_updates()
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nBot shutdown requested. Exiting gracefully...")
        logger.info("Bot shutdown requested")

    except Exception as e:
        print(f"Error starting bot: {str(e)}")
        logger.error(f"Bot startup error: {str(e)}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
