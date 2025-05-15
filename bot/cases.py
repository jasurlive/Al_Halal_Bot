# bot/cases.py
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from bot.utils import send_image_with_caption
from bot.firebase import save_user_info, get_user_chat_info
from bot.keyboards import main_menu_keyboard
import os

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))  # Default to 0 if not set

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id
    logger.info(f"/start command received from user_id={user_id}, chat_id={chat_id}")

    try:
        await update.message.reply_text(
            "Welcome! Choose an option below:",
            reply_markup=main_menu_keyboard(),
        )
        save_user_info(user_id, chat_id)
        nickname = user.username or "N/A"
        profile_link = f"https://t.me/user?id={user_id}"
        report = (
            f"📥 *New User Started Bot:*\n"
            f"🆔 ID: `{user_id}`\n"
            f"🔗 [Profile]({profile_link})"
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=report,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
        logger.info(f"Admin notified about new user: {user_id}")
    except Exception as e:
        logger.error(f"Error in start handler: {e}", exc_info=True)
        await update.message.reply_text("❌ An error occurred during start.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text
    logger.info(f"Message from user_id={user_id}: {text}")

    try:
        if text == "📍 Address" or text == "📍 Location":
            await send_image_with_caption(
                update,
                context,
                "assets/img/bot.png",
                "📍 We're located at: 123 Market St, Townsville",
            )
            logger.info("Sent address info to user.")
        elif text == "☎ Contact":
            await update.message.reply_text(
                "✉️ Please send your message, and the admin will reply here."
            )
            save_user_info(user_id, chat_id)
            logger.info("Prompted user for contact message.")
        else:
            await context.bot.forward_message(
                chat_id=ADMIN_CHAT_ID,
                from_chat_id=chat_id,
                message_id=update.message.message_id,
            )
            await update.message.reply_text("✅ Message sent to the admin.")
            logger.info(f"Forwarded message from user_id={user_id} to admin.")
    except Exception as e:
        logger.error(f"Error in handle_message: {e}", exc_info=True)
        await update.message.reply_text("❌ Failed to process your request.")


async def forward_from_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID or not update.message.reply_to_message:
        logger.debug("forward_from_admin called from non-admin or without reply.")
        return

    try:
        replied_msg = update.message.reply_to_message
        original_sender_id = (
            replied_msg.forward_from.id if replied_msg.forward_from else None
        )
        if not original_sender_id:
            await update.message.reply_text("⚠️ Can't detect original sender.")
            logger.warning("Original sender not found in admin reply.")
            return

        user_data = get_user_chat_info(original_sender_id)
        if not user_data:
            await update.message.reply_text("⚠️ No stored chat ID for this user.")
            logger.warning(f"No chat info for user_id={original_sender_id}")
            return

        await context.bot.send_message(
            chat_id=user_data["chat_id"], text=update.message.text
        )
        logger.info(f"Admin reply forwarded to user_id={original_sender_id}")
    except Exception as e:
        logger.error(f"Error in forward_from_admin: {e}", exc_info=True)
        await update.message.reply_text("❌ Couldn't forward the message to user.")


def setup_cases(application: Application):
    logger.info("Setting up bot handlers.")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Chat(chat_id=ADMIN_CHAT_ID), forward_from_admin
        )
    )
