# bot/keyboards.py
from telegram import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📍 Location"), KeyboardButton("☎ Contact")],
        [KeyboardButton("🛒 Book Items"), KeyboardButton("🌐 Website")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
