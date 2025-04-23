# bot/admin.py
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext

# === Dictionary to track forwarded booking messages ===
# Maps admin's message_id (forwarded one) to user's chat_id and original message_id
forwarded_messages = {}


# === Called when admin replies to a forwarded message ===
def handle_admin_reply(update: Update, context: CallbackContext):
    message = update.message

    if not message.reply_to_message:
        return

    replied_msg = message.reply_to_message

    # Find original user and message from tracking dictionary
    if replied_msg.message_id in forwarded_messages:
        user_info = forwarded_messages[replied_msg.message_id]
        user_chat_id = user_info["chat_id"]
        user_msg_id = user_info["message_id"]

        # Send a reply back to the user referencing their original message
        context.bot.send_message(
            chat_id=user_chat_id,
            text=f"🛎 Admin reply:\n{message.text}",
            reply_to_message_id=user_msg_id,
        )


# === Called from cases.py when forwarding a booking ===
# You should call this function there to track the forwarding
def track_forwarded_message(admin_msg_id, user_chat_id, user_msg_id):
    # Store the mapping for replies
    forwarded_messages[admin_msg_id] = {
        "chat_id": user_chat_id,
        "message_id": user_msg_id,
    }


# === Register this in your main setup function ===
def setup_admin(dispatcher):
    dispatcher.add_handler(
        MessageHandler(Filters.reply & Filters.text, handle_admin_reply)
    )
