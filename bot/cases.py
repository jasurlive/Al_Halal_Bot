# bot/cases.py
from telegram import Update, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption
from dotenv import load_dotenv
import os

load_dotenv()

# === Admin ID (loaded from .env) ===
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))


def start(update: Update, context: CallbackContext):
    user = update.effective_user

    # Send welcome message to the user
    update.message.reply_text(
        "Welcome to the Market Bot! Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )

    # === BEGIN: One-time user report to admin ===
    first_name = user.first_name or "N/A"
    user_id = user.id
    nickname = user.username or "N/A"
    is_bot = user.is_bot
    profile_link = f"https://t.me/{nickname}" if nickname != "N/A" else "N/A"

    report_text = (
        f"📋 *User Report:*\n"
        f"👤 Name: {first_name}\n"
        f"🆔 User ID: `{user_id}`\n"
        f"🔖 Nickname: @{nickname}\n"
        f"🔗 Profile: [Link to profile]({profile_link})\n"
        f"🤖 Bot: {'Yes' if is_bot else 'No'}"
    )

    try:
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=report_text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"Failed to send user report to admin: {e}")
    # === END: One-time user report to admin ===


def handle_message(update: Update, context: CallbackContext):
    # Get the text message the user sent
    text = update.message.text

    # If the user sends a text message, handle the usual responses
    if text == "📍 Location":
        send_image_with_caption(
            update,
            context,
            "assets/img/bot.png",
            "📍 We're located at: 123 Market St, Townsville",
        )
    elif text == "☎ Contact":
        send_image_with_caption(
            update, context, "assets/img/bot.png", "📞 Contact us at: +123 456 789"
        )
    elif text == "🛒 Book Items":
        update.message.reply_text(
            "📝 Please reply to this message with the item(s) you wish to book.\n"
            "Include quantity, preferred time, and any special requests."
        )
    elif text == "🌐 Website":
        send_image_with_caption(
            update,
            context,
            "assets/img/bot.png",
            "🌐 Visit our site: https://example.com",
        )
    else:
        update.message.reply_text("Please select an option from the keyboard.")


# === Forward all user messages to admin ===
def forward_all_messages(update: Update, context: CallbackContext):
    message = update.message

    try:
        # Forward the message to the admin
        context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
        )
        # Acknowledge to the user that their message was forwarded
        update.message.reply_text("✅ Your message has been forwarded to the admin!")

    except Exception as e:
        # Handle any errors during forwarding
        print(f"Error forwarding message: {e}")
        update.message.reply_text(
            "❌ Sorry, there was an error while sending your message."
        )


def setup_cases(dispatcher):
    # Add the handler for forwarding all messages (text, files, GIFs, etc.)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )

    # Add the generic handler for forwarding all other messages (files, images, videos, etc.)
    dispatcher.add_handler(MessageHandler(Filters.all, forward_all_messages))
