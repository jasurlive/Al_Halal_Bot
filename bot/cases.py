import logging
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ADMIN_CHAT_ID = 5840967881
user_chat_dict = {}  # Dictionary to store user chat IDs for reply mapping


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Market Bot! Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )
    logger.info(f"Start command triggered by user {update.message.chat_id}")


def handle_message(update: Update, context: CallbackContext):
    user_chat_id = update.message.chat_id

    # Avoid forwarding messages from admin to the admin
    if user_chat_id == ADMIN_CHAT_ID:
        logger.info(f"Admin message from {ADMIN_CHAT_ID} ignored.")
        return

    user_chat_dict[user_chat_id] = user_chat_id
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
        logger.info(
            f"Message from user {user_chat_id} forwarded to admin {ADMIN_CHAT_ID}."
        )
    except Exception as e:
        logger.error(f"Error forwarding message from user {user_chat_id}: {e}")
        update.message.reply_text(
            "❌ Sorry, there was an error while sending your message."
        )


def handle_admin_reply(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        user_chat_id = (
            update.message.reply_to_message.forward_from.id
        )  # Get the user ID from the admin reply
        logger.info(f"Admin replied to user {user_chat_id}.")

        # Ensure the user exists in the dictionary
        if user_chat_id in user_chat_dict:
            try:
                # Send the admin reply to the correct user
                context.bot.send_message(chat_id=user_chat_id, text=update.message.text)
                update.message.reply_text("✅ Your reply has been sent to the user!")
                logger.info(f"Admin reply sent to user {user_chat_id}.")
            except Exception as e:
                logger.error(f"Error sending reply to user {user_chat_id}: {e}")
                update.message.reply_text(
                    "❌ Sorry, there was an error while sending your reply."
                )
        else:
            logger.warning(f"User {user_chat_id} not found for reply.")
            update.message.reply_text("❌ User not found for this reply.")
    else:
        logger.warning(
            f"Admin message was not a reply. Admin chat ID: {update.message.chat_id}"
        )
        update.message.reply_text("❌ Please reply to a user's message to forward it.")


def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.text & Filters.reply, handle_admin_reply)
    )  # Admin reply handling
