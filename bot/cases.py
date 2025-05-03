# bot/cases.py
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from bot.utils import send_image_with_caption
from bot.firebase import save_user_info, get_user_chat_info
from dotenv import load_dotenv
import os

load_dotenv()

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))


# === Custom Keyboard ===
def main_menu_keyboard():
    keyboard = [[KeyboardButton("📍 Address")], [KeyboardButton("☎ Contact")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id

    await update.message.reply_text(
        "Welcome! Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )

    # Save user info for message routing
    save_user_info(user_id, chat_id)

    # Report to admin
    nickname = user.username or "N/A"
    profile_link = f"https://t.me/{nickname}" if nickname != "N/A" else "N/A"
    report = (
        f"📥 *New User Started Bot:*\n"
        f"🆔 ID: `{user_id}`\n"
        f"🔗 [Profile]({profile_link})"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=report,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"Admin notification failed: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text

    if text == "📍 Address":
        await send_image_with_caption(
            update,
            context,
            "assets/img/bot.png",
            "📍 We're located at: 123 Market St, Townsville",
        )
    elif text == "☎ Contact":
        await update.message.reply_text(
            "✉️ Please send your message, and the admin will reply here."
        )
        save_user_info(user_id, chat_id)
    else:
        try:
            await context.bot.forward_message(
                chat_id=ADMIN_CHAT_ID,
                from_chat_id=chat_id,
                message_id=update.message.message_id,
            )
            await update.message.reply_text("✅ Message sent to the admin.")
        except Exception as e:
            print(f"Forwarding failed: {e}")
            await update.message.reply_text(
                "❌ Failed to send your message to the admin."
            )


async def forward_from_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID or not update.message.reply_to_message:
        return

    try:
        replied_msg = update.message.reply_to_message
        original_sender_id = (
            replied_msg.forward_from.id if replied_msg.forward_from else None
        )

        if not original_sender_id:
            await update.message.reply_text("⚠️ Can't detect original sender.")
            return

        user_data = get_user_chat_info(original_sender_id)
        if not user_data:
            await update.message.reply_text("⚠️ No stored chat ID for this user.")
            return

        await context.bot.send_message(
            chat_id=user_data["chat_id"], text=update.message.text
        )
    except Exception as e:
        print(f"Admin reply failed: {e}")
        await update.message.reply_text("❌ Couldn't forward the message to user.")


def setup_cases(application: Application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Chat(chat_id=ADMIN_CHAT_ID), forward_from_admin
        )
    )
