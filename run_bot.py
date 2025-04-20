import asyncio
from project.bot.handlers import start
from project.bot.handlers.start import router
from project.bot.keyboards.botCommands import set_bot_commands
from aiogram import Bot, Dispatcher


bot = Bot("7938224331:AAGw75HUIxB9paXt5VWM_F7VpNPiy5KHio4")
dp = Dispatcher()

async def main():
    dp.include_router(router)
    await set_bot_commands(bot)
    await dp.start_polling(bot)
    print("bot started...")
asyncio.run(main())