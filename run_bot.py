import asyncio
from project.bot.handlers import start
from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher
from project.bot.handlers.start import router
bot = Bot(token="7938224331:AAGw75HUIxB9paXt5VWM_F7VpNPiy5KHio4")
dp = Dispatcher()
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/restart", description="Перезапустить бота"),
    ]
    await bot.set_my_commands(commands)
async def main():
    dp.include_router(router)
    await set_bot_commands(bot)
    await dp.start_polling(bot)
    print("bot started...")
asyncio.run(main())