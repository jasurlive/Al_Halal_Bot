from telegram import Update, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption

ADMIN_CHAT_ID = 5840967881


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


def forward_all_messages(update: Update, context: CallbackContext):
    message = update.message
    try:
        context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
        )
        update.message.reply_text("✅ Your message has been forwarded to the admin!")
    except Exception as e:
        print(f"Error forwarding message: {e}")
        update.message.reply_text(
            "❌ Sorry, there was an error while sending your message."
        )


def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )
    dispatcher.add_handler(MessageHandler(Filters.all, forward_all_messages))
