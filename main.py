import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application
from bot import bot
from bot.cases import setup_cases
import os
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is not set in environment variables.")
    raise RuntimeError("BOT_TOKEN is required.")

application = Application.builder().token(BOT_TOKEN).build()
setup_cases(application)


@app.post("/")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.debug(f"Incoming Telegram Update: {data}")
        update = Update.de_json(data, bot)
        await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in webhook: {e}\n{traceback.format_exc()}")
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
