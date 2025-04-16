import asyncio
from project.bot.handlers import start
from aiogram import Bot, Dispatcher
from project.bot.handlers.start import router
bot = Bot(token="7938224331:AAGw75HUIxB9paXt5VWM_F7VpNPiy5KHio4")
dp = Dispatcher()

async def main():
    dp.include_router(router)
    
    await dp.start_polling(bot)
    print("bot started...")
asyncio.run(main())