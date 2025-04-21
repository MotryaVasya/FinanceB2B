from importlib.resources import read_text
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from project.bot.messages.messages import *
from aiogram.types import Message
from aiogram.filters import or_f

from project.bot.handlers.start import Context
from project.bot.keyboards.reply import (
    Money_keyboard,
    get_categories_keyboard,
    get_transaction_keyboard,
    help_keyboard,
)
router=Router()

@router.message(F.text == "Помощь")
async def help_handler(message: Message):
    try:
        await message.answer(
            read_text,
            reply_markup=await help_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text=="Баланс")
async def cash_handler(message: Message):
    text=(f"💫 Ваш баланс: \nУ тебя всё под контролем! 🧘‍♂️\n ")
    try:
        await message.answer(
            text,
            reply_markup=await Money_keyboard()
        )
        
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Категории")
async def categories_handler(message: Message, state: FSMContext):
    try:
        await state.set_state(Context.IN_CATEGORIES)
        await message.answer(
            cattegory_text,
            reply_markup=await get_categories_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(or_f(F.text == "Транзакция",F.text=="Перейти к транзакциям"))
async def transaction_handler(message: Message, state: FSMContext):
    try:
        await state.set_state(Context.IN_TRANSACTIONS)
        await message.answer(
            "Выберите действие с транзакциями:",
            reply_markup=await get_transaction_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")