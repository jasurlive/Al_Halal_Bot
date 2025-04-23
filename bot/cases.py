# bot/cases.py
from telegram import Update, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption

# === Admin ID (set your actual admin ID here) ===
ADMIN_CHAT_ID = 5840967881  # <-- Replace this with the actual admin ID


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Market Bot! Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )


def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

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


# === Forward user messages to admin ===
def forward_booking_reply(update: Update, context: CallbackContext):
    message = update.message

    # Check if the message is a reply to a booking message (optional, but helpful)
    if (
        message.reply_to_message
        and message.reply_to_message.text
        == "📝 Please reply to this message with the item(s) you wish to book."
    ):
        try:
            # Forward the user's reply to the admin
            context.bot.forward_message(
                chat_id=ADMIN_CHAT_ID,
                from_chat_id=message.chat_id,
                message_id=message.message_id,
            )
            # Confirm to the user that their message has been sent
            message.reply_text("✅ Your booking request has been sent to the admin!")
        except Exception as e:
            # Log any errors encountered during forwarding
            print(f"Error forwarding message: {e}")
            message.reply_text(
                "❌ Sorry, there was an error while sending your booking request."
            )
    else:
        # If it's not a reply to the booking message
        message.reply_text(
            "⚠️ Please reply to the booking request message to send your request to the admin."
        )


def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )

    # === Handler for replies to booking message ===
    dispatcher.add_handler(
        MessageHandler(Filters.reply & Filters.text, forward_booking_reply)
    )
