import logging
import os
import traceback
from telegram import Update
from telegram.ext import Application
from bot import bot
from bot.cases import setup_cases

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

_initialized = False


async def handler(request):
    global _initialized
    try:
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

        if not _initialized:
            await application.initialize()
            _initialized = True

        await application.process_update(update)
        logger.info("Update processed successfully.")
        return {"statusCode": 200, "body": "ok"}
    except Exception as e:
        logger.error(f"Error in webhook: {e}\n{traceback.format_exc()}")
        return {"statusCode": 200, "body": "error"}
