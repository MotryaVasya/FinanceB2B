from aiogram.types import BotCommand
from aiogram import Bot

async def set_bot_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/restart", description="Перезапустить бота"),
    ]
    await bot.set_my_commands(commands)