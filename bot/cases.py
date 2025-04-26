# bot/cases.py
from telegram import Update, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from bot.keyboards import main_menu_keyboard
from bot.utils import send_image_with_caption

ADMIN_CHAT_ID = 5840967881

user_template_message_ids = {}
forwarded_message_map = {}


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Market Bot! Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )


def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.effective_chat.id

    if text == " Location":
        send_image_with_caption(
            update,
            context,
            "assets/img/bot.png",
            " We're located at: 123 Market St, Townsville",
        )
    elif text == " Contact":
        send_image_with_caption(
            update, context, "assets/img/bot.png", " Contact us at: +123 456 789"
        )
    elif text == " Book Items":
        sent = update.message.reply_text(
            " Please reply to this message with the item(s) you wish to book.\n"
            "Include quantity, preferred time, and any special requests."
        )
        user_template_message_ids[chat_id] = sent.message_id
    elif text == " Website":
        send_image_with_caption(
            update,
            context,
            "assets/img/bot.png",
            " Visit our site: https://example.com",
        )
    else:
        update.message.reply_text("Please select an option from the keyboard.")


def forward_booking_reply(update: Update, context: CallbackContext):
    message = update.message
    user_chat_id = update.effective_chat.id
    user_message_id = message.message_id

    # 🛠️ SAFELY ADDED: Ignore admin messages here to avoid duplicate handling
    if user_chat_id == ADMIN_CHAT_ID:
        return

    forwarded = context.bot.forward_message(
        chat_id=ADMIN_CHAT_ID,
        from_chat_id=user_chat_id,
        message_id=user_message_id,
    )

    # Store the mapping for admin replies
    forwarded_message_map[forwarded.message_id] = (user_chat_id, user_message_id)
    message.reply_text("Your message has been sent to the admin!")


def handle_admin_reply(update: Update, context: CallbackContext):
    message = update.message

    # 🛠️ SAFELY ADDED: Only handle replies in admin chat
    if message.chat.id != ADMIN_CHAT_ID:
        return

    if message.reply_to_message:
        admin_reply_to_id = message.reply_to_message.message_id

        if admin_reply_to_id in forwarded_message_map:
            user_chat_id, user_message_id = forwarded_message_map[admin_reply_to_id]

            context.bot.send_message(
                chat_id=user_chat_id,
                text=message.text,
                reply_to_message_id=user_message_id,
            )


def setup_cases(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )
    # 🛠️ SAFELY UPDATED: Forward only user replies
    dispatcher.add_handler(
        MessageHandler(
            Filters.reply & Filters.text & ~Filters.chat(chat_id=ADMIN_CHAT_ID),
            forward_booking_reply,
        )
    )
    # 🛠️ SAFELY UPDATED: Admin reply handler (must come after to override properly)
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & Filters.reply & Filters.chat(chat_id=ADMIN_CHAT_ID),
            handle_admin_reply,
        )
    )
