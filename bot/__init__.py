# bot/__init__.py
import os
from dotenv import load_dotenv
from telegram import Bot
import logging

# Load .env if running locally
load_dotenv()

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is not set in environment variables.")
    raise RuntimeError("BOT_TOKEN is required.")

bot = Bot(token=BOT_TOKEN)
logger.info("Telegram Bot initialized.")
