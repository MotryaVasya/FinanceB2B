from aiogram import types, F
from project.bot.bot import dp

@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    await message.answer("Привет! Я твой бот")