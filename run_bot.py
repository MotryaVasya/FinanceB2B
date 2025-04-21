import asyncio
from aiogram import Bot, Dispatcher
from project.bot.handlers.menu import router as menu_router 
from project.bot.handlers.start import router as start_router
from project.bot.handlers.categories import router as categories_router
from project.bot.handlers.transactions import router as transactions_router
from project.bot.handlers.balance import router as balance_router
from project.bot.keyboards.botCommands import set_bot_commands
from project.core.config import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(menu_router)
    dp.include_router(start_router)
    dp.include_router(balance_router)
    dp.include_router(categories_router)
    dp.include_router(transactions_router)
    await set_bot_commands(bot)
    
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())