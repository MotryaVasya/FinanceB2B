import asyncio
from project.bot.handlers import start
from aiogram import Bot, Dispatcher
from project.bot.handlers.start import router

bot = Bot(token="8042268635:AAG0W_I8n8QZK3oQJYs9I3h_Rr4ALnsvjhk")
dp = Dispatcher()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)
asyncio.run(main())