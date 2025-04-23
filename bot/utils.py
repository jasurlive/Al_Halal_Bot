# bot/utils.py
from telegram import Update
from telegram.ext import CallbackContext


def send_image_with_caption(
    update: Update, context: CallbackContext, image_path: str, caption: str
):
    with open(image_path, "rb") as photo:
        update.message.reply_photo(photo=photo, caption=caption)
