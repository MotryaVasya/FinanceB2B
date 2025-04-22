import asyncio
import logging
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


async def start():
    dp.include_router(menu_router)
    dp.include_router(start_router)
    dp.include_router(balance_router)
    dp.include_router(categories_router)
    dp.include_router(transactions_router)
    await set_bot_commands(bot)
    
    # print("Bot started...")
    # print("gawgwa")
    # await dp.start_polling(bot)


async def on_startup():
    logging.info("🚀 Starting application")
    await start()
    if config.DEBUG:
        _ = asyncio.create_task(
            dp.start_polling(
                bot,
                polling_timeout=30,
                handle_signals=False,
                allowed_updates=dp.resolve_used_update_types(),
            )
        )
    # else:
    #     WEBHOOK_PATH = f"webhook/{settings.BOT_TOKEN}"
    #     await bot.set_webhook(
    #         f"https://{settings.DOMAIN}/{WEBHOOK_PATH}",
    #         allowed_updates=dp.resolve_used_update_types(),
    #     )


async def on_shutdown():
    if config.DEBUG:
        await dp.stop_polling()
    # else:
    #     await dp.delete_webhook()
    # logging.info("⛔️ Stop bot")
    # logging.info("⛔️ Stop application"
