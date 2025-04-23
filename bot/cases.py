from telegram import Update, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption

# === Admin ID (set your actual admin ID here) ===
ADMIN_CHAT_ID = 5840967881  # <-- Replace this with the actual admin ID

# Temporary storage for users currently in contact with the admin
user_to_admin_message = {}


def start(update: Update, context: CallbackContext):
    user = update.effective_user

    # Send welcome message to the user
    update.message.reply_text(
        "Welcome to the new Al Halal Market Bot! Choose an option below:",
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

    # If the message is from the admin, do nothing here
    if update.message.chat_id == ADMIN_CHAT_ID:
        # Admin's reply will be handled in the relay_admin_reply function
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
        forward_message_to_admin(update, context)
        return  # Ensure we don't proceed with the "Please select an option" reply


def forward_message_to_admin(update: Update, context: CallbackContext):
    message = update.message

    # Check if the message is from the admin, and ignore it if it is
    if message.chat_id == ADMIN_CHAT_ID:
        return

    try:
        # Forward the message to the admin
        forwarded_message = context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
        )

        # Track the user sending the message
        user_to_admin_message[message.message_id] = message.chat_id

        # Send a confirmation to the user
        update.message.reply_text("✅ Your message has been forwarded to the admin!")

    except Exception as e:
        print(f"Error forwarding message: {e}")
        update.message.reply_text(
            "❌ Sorry, there was an error while sending your message."
        )


# === Begin: Relay admin reply to the user ===
def relay_admin_reply(update: Update, context: CallbackContext):
    message = update.message

    # Only handle replies from the admin
    if message.chat_id != ADMIN_CHAT_ID:
        return

    # Ensure that the admin's message is a reply to a forwarded message
    if (
        message.reply_to_message
        and message.reply_to_message.message_id in user_to_admin_message
    ):
        original_user_chat_id = user_to_admin_message[
            message.reply_to_message.message_id
        ]

        try:
            # Forward admin's reply to the user
            if message.text:
                context.bot.send_message(
                    chat_id=original_user_chat_id, text=message.text
                )

            # Handle media (photo, video, etc.)
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

            # You can handle other media types in a similar manner...

            # Confirmation to the admin
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


# Setup handlers
def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )
    dispatcher.add_handler(MessageHandler(Filters.all, forward_message_to_admin))

    # Register handler for admin replies
    dispatcher.add_handler(
        MessageHandler(Filters.reply & Filters.chat(ADMIN_CHAT_ID), relay_admin_reply)
    )
