from importlib.resources import read_text
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from project.bot.messages.messages import *
from aiogram.types import Message
from aiogram.filters import or_f, Command
from project.bot.states import *
from project.bot.Save import save
from project.bot.handlers.start import Context
import logging
from project.bot.keyboards.reply import (
    Money_keyboard,
    get_categories_keyboard,
    get_transaction_keyboard,
    help_keyboard,
)
from project.db.session import drop_db
router=Router()
from project.bot.conecting_methods.user import get_user
@router.message(F.text == "Помощь")
async def help_handler(message: Message,state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(Context.popa)
    open("categories.txt", "w").write(str(await save.update(user_id, "MAIN_HELP")))
    try:
        await message.answer(
            help_text,
            reply_markup=await help_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(or_f(F.text=="Перейти в меню"),Context.popa)
async def start_handler_for_help(message: Message,state: FSMContext):
    try:
        await state.clear()
        await message.answer(
            pre_help,
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")

@router.message(or_f(F.text == "Баланс", F.text=="Вернутся к балансу"))
async def cash_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(Context.biba)

    data = await get_user(user_id)
    text = "💫 Ваш баланс: {"+str(data['cash'])+"}\n"
    open("balance.txt", "w").write(str(await save.update(user_id, "BALANCE")))
    open("main44.txt", "w").write(str(await save.convert_to_json()))
    try:
        await message.answer(
            text,
            reply_markup=await Money_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Категории")
async def categories_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("categories.txt", "w").write(str(await save.update(user_id, "MAIN_CATEGORY")))
    try:
        await state.set_state(CategoryStates.in_categorie)
        await message.answer(
            cattegory_text,
            reply_markup=await get_categories_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(or_f(F.text == "Мои записи", F.text == "Перейти к моим записям"))
async def transaction_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("main44.txt", "w").write(str(await save.update(user_id, "MAIN_TRANSACTIONS")))
    try:
        await state.set_state(TransactionStates.in_transactions)
        await message.answer(
            text=trasaction_actions,
            reply_markup=await get_transaction_keyboard())
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(Command('drop'))
async def drop_database(message: Message):
    await drop_db()