# bot/keyboards.py
from telegram import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📍 Address")],
        [KeyboardButton("☎ Contact")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
