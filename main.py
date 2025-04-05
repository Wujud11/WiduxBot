
from app import app
from bot import start_bot
import threading
import logging
import os

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_bot():
    """Run the Twitch bot in a separate thread"""
    try:
        logger.info("Starting Twitch bot...")
        start_bot()
        logger.info("Bot is now running!")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        logger.error(traceback.format_exc())

# Initialize bot thread variable to be started later
bot_thread = None

def start_bot_thread():
    """Start the bot in a background thread"""
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        logger.info("Bot thread started from main module.")

# Export app for gunicorn
app = app

if __name__ == "__main__":
    # Start the Flask app
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask app on port {port}...")
    app.run(host="0.0.0.0", port=port)
