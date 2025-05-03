import logging
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.storage_firebase import (
    add_user_chat,
    get_user_chat,
)  # ✅ Firebase-based storage

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ADMIN_CHAT_ID = 5840967881  # Admin chat ID


def start(update: Update, context: CallbackContext):
    user_chat_id = update.message.chat_id
    update.message.reply_text(
        "Welcome to the Market Bot! Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )
    logger.info(f"Start command triggered by user {user_chat_id}")


def forward_to_admin(update: Update, context: CallbackContext):
    """Forward user messages to the admin."""
    user_chat_id = update.message.chat_id

    # Ignore messages from the admin
    if user_chat_id == ADMIN_CHAT_ID:
        return

    # Store the user's chat ID in Firebase
    add_user_chat(user_chat_id)
    logger.info(
        f"Forwarding message from user {user_chat_id} to admin {ADMIN_CHAT_ID}."
    )

    try:
        context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=user_chat_id,
            message_id=update.message.message_id,
        )
        update.message.reply_text("✅ Your message has been forwarded to the admin!")
        logger.info(f"Message from user {user_chat_id} forwarded to admin.")
    except Exception as e:
        logger.error(f"Error forwarding message from user {user_chat_id}: {e}")
        update.message.reply_text(
            "❌ Sorry, there was an error while sending your message."
        )


def handle_admin_reply(update: Update, context: CallbackContext):
    """Handle admin replies and send them to the correct user."""
    if update.message.reply_to_message:
        original_message = update.message.reply_to_message

        if original_message.forward_from:
            user_chat_id = original_message.forward_from.id
            logger.info(f"Admin replied to user {user_chat_id}.")

            if get_user_chat(user_chat_id):  # ✅ Check against Firebase
                try:
                    context.bot.send_message(
                        chat_id=user_chat_id, text=update.message.text
                    )
                    update.message.reply_text(
                        f"✅ Your reply has been sent to user {user_chat_id}!"
                    )
                    logger.info(f"Admin reply sent to user {user_chat_id}.")
                except Exception as e:
                    logger.error(f"Error sending reply to user {user_chat_id}: {e}")
                    update.message.reply_text(
                        f"❌ Error sending your reply to user {user_chat_id}."
                    )
            else:
                logger.warning(f"User {user_chat_id} not found in Firebase.")
                update.message.reply_text(
                    f"❌ User {user_chat_id} not found for this reply."
                )
        else:
            logger.warning("Admin's reply is not to a valid user message.")
            update.message.reply_text(
                "❌ Admin's reply is not to a valid user message."
            )
    else:
        logger.warning("Admin message was not a reply.")
        update.message.reply_text("❌ Please reply to a user's message to forward it.")


def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, forward_to_admin)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.text & Filters.reply, handle_admin_reply)
    )
