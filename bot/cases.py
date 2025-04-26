from telegram import Update, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption
import logging

# === Constants ===
ADMIN_CHAT_ID = 5840967881  # Replace this with your real Telegram admin user ID

# === Setup logging ===
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# === /start command ===
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Market Bot! Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )


# === User interaction handler ===
def handle_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    text = update.message.text

    logger.debug(f"Received message: {text} from user: {user.id} ({user.username})")

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
        update.message.reply_text("✅ Your message has been sent!")
        try:
            context.bot.forward_message(
                chat_id=ADMIN_CHAT_ID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id,
            )
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            update.message.reply_text(
                "❌ Sorry, there was an error while sending your message."
            )


# === Admin reply forwarding logic ===
def forward_all_messages(update: Update, context: CallbackContext):
    message = update.message
    user = message.from_user

    # === Handle admin reply ===
    if (
        user.id == ADMIN_CHAT_ID
        and message.reply_to_message
        and message.reply_to_message.forward_from
    ):
        original = message.reply_to_message
        target_user_id = original.forward_from.id

        if target_user_id != ADMIN_CHAT_ID:
            logger.debug(f"Admin replying to message from user: {target_user_id}")

            try:
                if message.text:
                    context.bot.send_message(chat_id=target_user_id, text=message.text)

                elif message.photo:
                    context.bot.send_photo(
                        chat_id=target_user_id,
                        photo=message.photo[-1].file_id,
                        caption=message.caption or None,
                    )

                elif message.document:
                    context.bot.send_document(
                        chat_id=target_user_id,
                        document=message.document.file_id,
                        caption=message.caption or None,
                    )

                elif message.video:
                    context.bot.send_video(
                        chat_id=target_user_id,
                        video=message.video.file_id,
                        caption=message.caption or None,
                    )

                elif message.audio:
                    context.bot.send_audio(
                        chat_id=target_user_id,
                        audio=message.audio.file_id,
                        caption=message.caption or None,
                    )

                elif message.voice:
                    context.bot.send_voice(
                        chat_id=target_user_id,
                        voice=message.voice.file_id,
                        caption=message.caption or None,
                    )

                elif message.sticker:
                    context.bot.send_sticker(
                        chat_id=target_user_id,
                        sticker=message.sticker.file_id,
                    )

                else:
                    update.message.reply_text("⚠️ Unsupported message type.")

                update.message.reply_text("✅ Message sent to the user!")

            except Exception as e:
                logger.error(
                    f"[Error] Couldn't send reply to user {target_user_id}: {e}"
                )
                update.message.reply_text("❌ Failed to send message to the user.")
        return  # === Exit to avoid double forwarding

    # === Ignore any non-reply admin messages ===
    if user.id == ADMIN_CHAT_ID:
        logger.debug("Admin sent a non-reply message. Ignoring.")
        return

    # === Forward regular user message to admin ===
    try:
        context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
        )
        update.message.reply_text("✅ Your message has been forwarded to the admin!")
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        update.message.reply_text(
            "❌ Sorry, there was an error while sending your message."
        )


# === Register bot handlers ===
def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))

    # === ✅ Ensure admin replies are caught first
    dispatcher.add_handler(MessageHandler(Filters.all, forward_all_messages), group=0)

    # === ✅ Handle user interactions
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message), group=1
    )
