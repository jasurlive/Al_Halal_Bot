import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.cases import setup_cases
from bot.firebase import save_user_info, get_user_chat_info

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is not set in environment variables.")
    raise RuntimeError("BOT_TOKEN is required.")


async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    setup_cases(application)
    logger.info("Bot started in polling mode.")
    await application.run_polling()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
