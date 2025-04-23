# bot/__init__.py
import os
from dotenv import load_dotenv
from telegram import Bot

# Load .env if running locally
load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
