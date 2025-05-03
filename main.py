from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application
from bot import bot
from bot.cases import setup_cases

import logging

app = FastAPI()

# Initialize Application instead of Dispatcher
application = Application.builder().token("YOUR_BOT_TOKEN").build()
setup_cases(application)


@app.post("/")
async def webhook(request: Request):
    try:
        # Extract the JSON data from the request
        data = await request.json()
        logging.warning("Incoming Telegram Update: %s", data)  # 🔍 Log payload

        # Create an Update object from the incoming data
        update = Update.de_json(data, bot)

        # Process the update using the Application's dispatcher
        application.update_queue.put(update)  # Queue the update for processing

        return {"status": "ok"}
    except Exception as e:
        logging.error("Error in webhook: %s", str(e))
        return {"status": "error", "message": str(e)}
