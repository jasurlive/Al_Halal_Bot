from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption

ADMIN_CHAT_ID = 5840967881
user_chat_dict = {}  # Dictionary to store user chat IDs for reply mapping


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Market Bot! Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )


def handle_message(update: Update, context: CallbackContext):
    # Save the user's chat ID for admin replies
    user_chat_dict[update.message.chat_id] = update.message.chat_id

    # Forward the message to the admin
    context.bot.forward_message(
        chat_id=ADMIN_CHAT_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id,
    )
    update.message.reply_text("✅ Your message has been forwarded to the admin!")


def handle_admin_reply(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        user_chat_id = (
            update.message.reply_to_message.forward_from.id
        )  # Get the user ID from the admin reply
        if user_chat_id in user_chat_dict:
            context.bot.send_message(
                chat_id=user_chat_dict[user_chat_id], text=update.message.text
            )
            update.message.reply_text("✅ Your reply has been sent to the user!")
        else:
            update.message.reply_text("❌ User not found for this reply.")
    else:
        update.message.reply_text("❌ Please reply to a user's message to forward it.")


def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.text & Filters.reply, handle_admin_reply)
    )  # Admin reply handling
