from telegram import Update, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption
import logging

# from firebase import log_user_message  # Uncomment if you're logging to Firestore

ADMIN_CHAT_ID = 5840967881

# === Setup logging ===
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Market Bot! Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )


def handle_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    text = update.message.text

    # === Optional: Log the message to Firebase ===
    # log_user_message(user.id, user.username or "NoUsername", text)

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
        # === Handle unknown message ===
        if user.id == ADMIN_CHAT_ID:
            update.message.reply_text("👋 Hey, admin! I got it!")
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


def forward_all_messages(update: Update, context: CallbackContext):
    message = update.message
    user = message.from_user

    # === Log message details ===
    logger.debug(f"Processing message from user {user.id} - Text: {message.text}")

    # === Check if the admin is replying to a user's message ===
    if message.reply_to_message and message.reply_to_message.forward_from:
        original = message.reply_to_message
        logger.debug(f"Admin replying to message from user: {original.forward_from.id}")

        # Check if the original message was forwarded from a user (not another admin)
        if original.forward_from and original.forward_from.id != ADMIN_CHAT_ID:
            target_user_id = original.forward_from.id

            try:
                # === Handle different message types ===
                if message.text:
                    context.bot.send_message(chat_id=target_user_id, text=message.text)
                    logger.debug(f"Sent text message to user {target_user_id}")

                elif message.photo:
                    context.bot.send_photo(
                        chat_id=target_user_id,
                        photo=message.photo[-1].file_id,
                        caption=message.caption if message.caption else None,
                    )
                    logger.debug(f"Sent photo to user {target_user_id}")

                elif message.document:
                    context.bot.send_document(
                        chat_id=target_user_id,
                        document=message.document.file_id,
                        caption=message.caption if message.caption else None,
                    )
                    logger.debug(f"Sent document to user {target_user_id}")

                elif message.video:
                    context.bot.send_video(
                        chat_id=target_user_id,
                        video=message.video.file_id,
                        caption=message.caption if message.caption else None,
                    )
                    logger.debug(f"Sent video to user {target_user_id}")

                elif message.audio:
                    context.bot.send_audio(
                        chat_id=target_user_id,
                        audio=message.audio.file_id,
                        caption=message.caption if message.caption else None,
                    )
                    logger.debug(f"Sent audio to user {target_user_id}")

                elif message.voice:
                    context.bot.send_voice(
                        chat_id=target_user_id,
                        voice=message.voice.file_id,
                        caption=message.caption if message.caption else None,
                    )
                    logger.debug(f"Sent voice message to user {target_user_id}")

                elif message.sticker:
                    context.bot.send_sticker(
                        chat_id=target_user_id,
                        sticker=message.sticker.file_id,
                    )
                    logger.debug(f"Sent sticker to user {target_user_id}")

                else:
                    update.message.reply_text("⚠️ Unsupported message type.")

                update.message.reply_text("✅ Message sent to the user!")
            except Exception as e:
                logger.error(
                    f"[Error] Couldn't send reply to user {target_user_id}: {e}"
                )
                update.message.reply_text("❌ Failed to send message to the user.")

            return

    # === Admin sends an unrelated message — no reply ===
    if user.id == ADMIN_CHAT_ID:
        logger.debug("Admin sent an unrelated message, replying with 'I got it!'")
        update.message.reply_text("👋 Hey, admin! I got it!")
        return

    # === Regular user message — forward to admin ===
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


def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )
    dispatcher.add_handler(MessageHandler(Filters.all, forward_all_messages))
