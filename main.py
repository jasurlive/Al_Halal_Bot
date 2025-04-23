from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Dispatcher
from bot import bot
from bot.handlers import setup_handlers

import logging

app = FastAPI()

dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
setup_handlers(dispatcher)


@app.post("/")
async def webhook(request: Request):
    try:
        data = await request.json()
        logging.warning("Incoming Telegram Update: %s", data)  # 🔍 Log payload
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logging.error("Error in webhook: %s", str(e))
        return {"status": "error", "message": str(e)}
