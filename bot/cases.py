from telegram import Update, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption

# === Admin ID (set your actual admin ID here) ===
ADMIN_CHAT_ID = 5840967881  # <-- Replace this with the actual admin ID

# State to track whether the admin is replying to a user's message
user_to_admin_message = {}


def start(update: Update, context: CallbackContext):
    user = update.effective_user

    # Send welcome message to the user
    update.message.reply_text(
        "Welcome to  the new Al Halal Market Bot! Choose an option below:",
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
    text = update.message.text

    # If the message is from the admin, respond accordingly
    if update.message.chat_id == ADMIN_CHAT_ID:
        # If the admin sends an unknown command, reply with "Hey admin"
        update.message.reply_text("Hey admin")
        return

    # Handle user messages for the usual responses
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
        # Forward any message that doesn't match a predefined option to the admin
        forward_all_messages(update, context)
        return  # Ensure we don't proceed with the "Please select an option" reply


# === Forward all user messages to admin (excluding admin messages) ===
def forward_all_messages(update: Update, context: CallbackContext):
    message = update.message

    # Check if the message is from the admin, and ignore it if it is
    if message.chat_id == ADMIN_CHAT_ID:
        return

    try:
        # Forward the message to the admin (this will now handle both text and media)
        forwarded_message = context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
        )

        # Store the original user and the forwarded message for tracking
        user_to_admin_message[message.message_id] = message.chat_id

        # Acknowledge to the user that their message was forwarded
        update.message.reply_text("✅ Your message has been forwarded to the admin!")

    except Exception as e:
        # Handle any errors during forwarding
        print(f"Error forwarding message: {e}")
        update.message.reply_text(
            "❌ Sorry, there was an error while sending your message."
        )


# === BEGIN: Relay admin reply to original user ===
def relay_admin_reply(update: Update, context: CallbackContext):
    message = update.message

    # Only handle replies sent by the admin
    if message.chat_id != ADMIN_CHAT_ID:
        return

    # Ensure it's a reply to a forwarded user message
    if (
        not message.reply_to_message
        or message.reply_to_message.message_id not in user_to_admin_message
    ):
        return

    original_user_chat_id = user_to_admin_message[message.reply_to_message.message_id]

    try:
        # Relay the admin reply back to the user
        if message.text:
            context.bot.send_message(chat_id=original_user_chat_id, text=message.text)

        elif message.photo:
            largest_photo = message.photo[-1]
            caption = message.caption if message.caption else ""
            context.bot.send_photo(
                chat_id=original_user_chat_id,
                photo=largest_photo.file_id,
                caption=caption,
            )

        elif message.video:
            caption = message.caption if message.caption else ""
            context.bot.send_video(
                chat_id=original_user_chat_id,
                video=message.video.file_id,
                caption=caption,
            )

        elif message.audio:
            context.bot.send_audio(
                chat_id=original_user_chat_id,
                audio=message.audio.file_id,
                caption=message.caption or "",
            )

        elif message.voice:
            context.bot.send_voice(
                chat_id=original_user_chat_id,
                voice=message.voice.file_id,
                caption=message.caption or "",
            )

        elif message.document:
            caption = message.caption if message.caption else ""
            context.bot.send_document(
                chat_id=original_user_chat_id,
                document=message.document.file_id,
                caption=caption,
            )

        elif message.sticker:
            context.bot.send_sticker(
                chat_id=original_user_chat_id, sticker=message.sticker.file_id
            )

        elif message.video_note:
            context.bot.send_video_note(
                chat_id=original_user_chat_id, video_note=message.video_note.file_id
            )

        else:
            print("Unsupported message type.")
            # Optionally send a fallback message here

        # Send confirmation to admin
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"✅ Your message has been sent to @{message.reply_to_message.from_user.username}.",
        )

    except Exception as e:
        print(f"Error relaying admin reply: {e}")
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"Error relaying message to user {original_user_chat_id}: {e}",
        )


# === END: Relay admin reply to original user ===


def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )
    dispatcher.add_handler(MessageHandler(Filters.all, forward_all_messages))

    # === BEGIN: Register relay for admin replies ===
    dispatcher.add_handler(
        MessageHandler(Filters.reply & Filters.chat(ADMIN_CHAT_ID), relay_admin_reply)
    )
    # === END: Register relay for admin replies ===
