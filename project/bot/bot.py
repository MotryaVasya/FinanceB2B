from aiogram import Bot, Dispatcher
from core.config import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()