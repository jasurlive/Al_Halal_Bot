import logging
import os
import traceback
from telegram import Update
from telegram.ext import Application
from bot import bot
from bot.cases import setup_cases

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is not set in environment variables.")
    raise RuntimeError("BOT_TOKEN is required.")

application = Application.builder().token(BOT_TOKEN).build()
setup_cases(application)

_initialized = False  # Add this flag


# Vercel entrypoint
async def handler(request):
    global _initialized
    try:
        # Vercel passes the request as an ASGI scope+receive/send, but with python3.9+ you can use .json()
        if request.method == "GET":
            return {"statusCode": 200, "body": "ok"}
        if request.method != "POST":
            return {"statusCode": 405, "body": "Method Not Allowed"}
        try:
            data = await request.json()
        except Exception as e:
            raw_body = await request.body()
            logger.error(f"Failed to parse JSON. Raw body: {raw_body}")
            return {"statusCode": 400, "body": "Invalid JSON"}
        logger.debug(f"Incoming Telegram Update JSON: {data}")
        update = Update.de_json(data, bot)
        logger.debug("Update object created successfully.")

        # Ensure Application is initialized
        if not _initialized:
            await application.initialize()
            _initialized = True

        await application.process_update(update)
        logger.info("Update processed successfully.")
        return {"statusCode": 200, "body": "ok"}
    except Exception as e:
        logger.error(f"Error in webhook: {e}\n{traceback.format_exc()}")
        # Always return 200 to Telegram to avoid webhook being disabled, but log the error
        return {"statusCode": 200, "body": "error"}
