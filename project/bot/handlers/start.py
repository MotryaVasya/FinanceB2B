from aiogram import Router, types, F
from aiogram.filters import CommandStart
router=Router()
@router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет! Я твой бот")