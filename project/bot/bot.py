from aiogram import Bot, Dispatcher
from app.core.config import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()