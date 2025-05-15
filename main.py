from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application
from bot import bot
from bot.cases import setup_cases

import logging
import os

app = FastAPI()

# Initialize Application instead of Dispatcher
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Make sure BOT_TOKEN is set in your environment
application = Application.builder().token(BOT_TOKEN).build()
setup_cases(application)


@app.post("/")
async def webhook(request: Request):
    try:
        # Extract the JSON data from the request
        data = await request.json()
        logging.warning("Incoming Telegram Update: %s", data)  # 🔍 Log payload

        # Create an Update object from the incoming data
        update = Update.de_json(data, bot)

        # Process the update using the Application's async method
        await application.process_update(update)

        return {"status": "ok"}
    except Exception as e:
        logging.error("Error in webhook: %s", str(e))
        return {"status": "error", "message": str(e)}
