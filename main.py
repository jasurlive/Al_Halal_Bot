# main.py
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Dispatcher
from bot import bot
from bot.handlers import setup_handlers

app = FastAPI()

# Reuse dispatcher with in-memory updates
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
setup_handlers(dispatcher)


@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return {"status": "ok"}
