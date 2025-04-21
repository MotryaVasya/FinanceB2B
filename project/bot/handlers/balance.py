from aiogram import Router, types, F
from aiogram.types import Message
from project.bot.messages.messages import *
from project.bot.keyboards.reply import (
    start_keyboard,
    Afteradd_keyboard
)

router=Router()
@router.message(F.text=="Пeрейти в меню")
async def start_handler_for_help(message: Message):
    try:
        await message.answer(
            text=pre_balance,
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text=="Пополнить")
async def  Add_money_handler(message: Message):
    text=(f"💰 Хотите пополнить баланс?\n 🏦 Перейдите в раздел Транзакции для пополнения! 💳📈\n ")
    try:
        await message.answer(
            text,
            reply_markup=await Afteradd_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")