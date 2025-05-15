# bot/utils.py
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def send_image_with_caption(
    update: Update, context: ContextTypes.DEFAULT_TYPE, image_path: str, caption: str
):
    try:
        with open(image_path, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=caption)
        logger.info(
            f"Sent image {image_path} with caption to user_id={update.effective_user.id}"
        )
    except Exception as e:
        logger.error(f"Failed to send image: {e}", exc_info=True)
        await update.message.reply_text("❌ Failed to send image.")
