from telegram import Update, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption
import logging

# from firebase import log_user_message  # Uncomment if you're logging to Firestore

ADMIN_CHAT_ID = 5840967881

# === Dictionary to track users contacting admin ===
user_contacting = {}  # {user_id: message_id}

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
        user_contacting[user.id] = None  # Track user wanting to contact admin
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
    elif user.id in user_contacting:
        # === Forward user's follow-up message to admin ===
        try:
            context.bot.forward_message(
                chat_id=ADMIN_CHAT_ID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id,
            )
            update.message.reply_text("✅ Your message has been sent to the admin!")
            user_contacting.pop(user.id, None)  # Clear contact session
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            update.message.reply_text(
                "❌ Sorry, there was an error while sending your message."
            )
    else:
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

    # === Check if the admin is replying to a user's message ===
    if message.reply_to_message and message.reply_to_message.forward_from:
        original = message.reply_to_message
        logger.debug(f"Admin replying to message from user: {original.forward_from.id}")

        if original.forward_from and original.forward_from.id != ADMIN_CHAT_ID:
            target_user_id = original.forward_from.id

            try:
                # === Handle different message types from admin to user ===
                if message.text:
                    context.bot.send_message(chat_id=target_user_id, text=message.text)
                elif message.photo:
                    context.bot.send_photo(
                        chat_id=target_user_id,
                        photo=message.photo[-1].file_id,
                        caption=message.caption if message.caption else None,
                    )
                elif message.document:
                    context.bot.send_document(
                        chat_id=target_user_id,
                        document=message.document.file_id,
                        caption=message.caption if message.caption else None,
                    )
                elif message.video:
                    context.bot.send_video(
                        chat_id=target_user_id,
                        video=message.video.file_id,
                        caption=message.caption if message.caption else None,
                    )
                elif message.audio:
                    context.bot.send_audio(
                        chat_id=target_user_id,
                        audio=message.audio.file_id,
                        caption=message.caption if message.caption else None,
                    )
                elif message.voice:
                    context.bot.send_voice(
                        chat_id=target_user_id,
                        voice=message.voice.file_id,
                        caption=message.caption if message.caption else None,
                    )
                elif message.sticker:
                    context.bot.send_sticker(
                        chat_id=target_user_id,
                        sticker=message.sticker.file_id,
                    )
                elif message.contact:
                    context.bot.send_contact(
                        chat_id=target_user_id,
                        phone_number=message.contact.phone_number,
                        first_name=message.contact.first_name,
                        last_name=message.contact.last_name or "",
                    )
                elif message.location:
                    context.bot.send_location(
                        chat_id=target_user_id,
                        latitude=message.location.latitude,
                        longitude=message.location.longitude,
                    )
                elif message.venue:
                    context.bot.send_venue(
                        chat_id=target_user_id,
                        latitude=message.venue.location.latitude,
                        longitude=message.venue.location.longitude,
                        title=message.venue.title,
                        address=message.venue.address,
                    )
                elif message.dice:
                    context.bot.send_dice(
                        chat_id=target_user_id,
                        emoji=message.dice.emoji,
                    )
                else:
                    update.message.reply_text("⚠️ Unsupported message type.")

                update.message.reply_text("✅ Message sent to the user!")
            except Exception as e:
                logger.error(
                    f"[Error] Couldn't send reply to user {target_user_id}: {e}"
                )
                update.message.reply_text("❌ Failed to send message to the user.")
            return

    # === Admin sent unrelated message ===
    if user.id == ADMIN_CHAT_ID:
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
