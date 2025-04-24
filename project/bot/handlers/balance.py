from aiogram import Router, types, F
from aiogram.types import Message
from project.bot.messages.messages import *
from project.bot.states import *
from aiogram.filters import or_f
from project.bot.Save import save
from project.bot.keyboards.reply import (
    start_keyboard,
    Afteradd_keyboard
)
router=Router()
@router.message(or_f(F.text=="Перейти в меню"),Context.biba)
async def start_handler_for_help(message: Message,state: FSMContext):
    try:
        state.clear()
        await message.answer(
            pre_balance,
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Пополнить")
async def Add_money_handler(message: Message):
    user_id = message.from_user.id 
    open("popolnit.txt","w").write(str(await save.update(user_id, "ADD_MONEY")))
    open("main44.txt","w").write(str(await save.convert_to_json()))
    text = ('💰 Хотите пополнить баланс?\n🏦 Перейдите в раздел "Мои записи" для пополнения! 💳📈\n ')
    try:
        await message.answer(
            text,
            reply_markup=await Afteradd_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")