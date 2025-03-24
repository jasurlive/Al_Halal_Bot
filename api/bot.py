from flask import Flask, request
import requests
import os
from telegram import KeyboardButton, ReplyKeyboardMarkup

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
TELEGRAM_API_URL_PHOTO = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            # Send the image with a description (caption) together
            send_photo_with_caption(
                chat_id,
                "https://example.com/welcome_image.jpg",
                "Welcome to the bot! Use the buttons below to interact.",
            )

            # Send the keyboard buttons after the image
            keyboard = [
                [KeyboardButton("Help"), KeyboardButton("Echo")],
                [KeyboardButton("Settings")],
            ]
            reply_markup = ReplyKeyboardMarkup(
                keyboard, one_time_keyboard=False, resize_keyboard=True
            )
            send_message(chat_id, "Select an option from below:", reply_markup)
        elif text == "/help":
            reply = "This is a simple bot. Just send a message and I'll repeat it!"
            send_message(chat_id, reply)
        elif text == "Help":
            reply = (
                "Here's how this bot works... Just send a message, and I'll repeat it!"
            )
            send_message(chat_id, reply)
        elif text == "Echo":
            reply = "Send me a message and I'll echo it back!"
            send_message(chat_id, reply)
        elif text == "Settings":
            reply = "Settings menu (this is just an example)."
            send_message(chat_id, reply)
        else:
            reply = f"You said: {text}"
            send_message(chat_id, reply)

    return {"status": "ok"}


def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup.to_dict()
    requests.post(TELEGRAM_API_URL, json=payload)


def send_photo_with_caption(chat_id, photo_url, caption):
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,  # Add the caption here (the description/message)
    }
    requests.post(TELEGRAM_API_URL_PHOTO, json=payload)


@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"


if __name__ == "__main__":
    app.run(debug=True)
