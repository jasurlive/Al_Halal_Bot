from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption

# === Admin ID (set your actual admin ID here) ===
ADMIN_CHAT_ID = 5840967881  # <-- Replace this with the actual admin ID


# === Start command handler ===
def start(update: Update, context: CallbackContext):
    user = update.effective_user

    # Send welcome message to the user
    update.message.reply_text(
        "Welcome to the new Al Halal Market Bot! Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )

    # === Report user to admin once on start ===
    first_name = user.first_name or "N/A"
    user_id = user.id
    nickname = user.username or "N/A"
    profile_link = f"https://t.me/{nickname}" if nickname != "N/A" else "N/A"

    report_text = (
        f"📋 *User Report:*\n"
        f"👤 Name: {first_name}\n"
        f"🆔 User ID: `{user_id}`\n"
        f"🔖 Nickname: @{nickname}\n"
        f"🔗 Profile: [Link to profile]({profile_link})\n"
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


# === Handle user messages and forward to admin ===
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    user_chat_id = update.message.chat_id

    # If the message is from the admin, do nothing
    if user_chat_id == ADMIN_CHAT_ID:
        return

    # Handle predefined options
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
        # Forward the message to the admin
        forward_message_to_admin(update, context)
        return


# === Forward all user messages to admin ===
def forward_message_to_admin(update: Update, context: CallbackContext):
    message = update.message

    # Forward the message to the admin
    try:
        forwarded_message = context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
        )

        # Save the original user chat ID in user_data for later use
        context.user_data["original_user_chat_id"] = message.chat_id

        # Notify the user their message is forwarded
        update.message.reply_text("✅ Your message has been forwarded to the admin!")

    except Exception as e:
        print(f"Error forwarding message: {e}")
        update.message.reply_text(
            "❌ Sorry, there was an error while sending your message."
        )


# === Relay admin reply to original user ===
def relay_admin_reply(update: Update, context: CallbackContext):
    message = update.message

    # Only handle replies from the admin
    if message.chat_id != ADMIN_CHAT_ID:
        return

    # Ensure the reply is linked to a forwarded message
    if message.reply_to_message and hasattr(message.reply_to_message, "from_user"):
        original_user_chat_id = context.user_data.get("original_user_chat_id")

        if original_user_chat_id:
            try:
                # Relay the admin reply back to the user
                if message.text:
                    context.bot.send_message(
                        chat_id=original_user_chat_id, text=message.text
                    )

                # Handle media (photo, video, etc.)
                elif message.photo:
                    largest_photo = message.photo[-1]
                    context.bot.send_photo(
                        chat_id=original_user_chat_id,
                        photo=largest_photo.file_id,
                        caption=message.caption or "",
                    )

                elif message.video:
                    context.bot.send_video(
                        chat_id=original_user_chat_id,
                        video=message.video.file_id,
                        caption=message.caption or "",
                    )

                # Send confirmation to admin
                context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"✅ Your message has been sent to the user.",
                )
            except Exception as e:
                print(f"Error relaying admin reply: {e}")
                context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"Error relaying message: {e}",
                )


# === Register handlers ===
def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )
    dispatcher.add_handler(MessageHandler(Filters.all, forward_message_to_admin))

    # Handle admin replies
    dispatcher.add_handler(
        MessageHandler(Filters.reply & Filters.chat(ADMIN_CHAT_ID), relay_admin_reply)
    )
