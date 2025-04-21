from aiogram import Router, F
from aiogram.types import Message
from project.bot.messages.messages import *
from aiogram.fsm.context import FSMContext
from project.bot.states import TransactionStates
from project.bot.keyboards.reply import *
\
router=Router()

@router.message(F.text == "Пропустить", TransactionStates.waiting_for_transaction_description)
async def handle_skip_description(message: Message, state: FSMContext):
    
    await state.update_data(transaction_description=None)
    await message.answer("🎉 Укажите сумму транзакции:")
    await state.set_state(TransactionStates.waiting_for_transaction_amount)


@router.message(TransactionStates.waiting_for_transaction_description)
async def handle_description_input(message: Message, state: FSMContext):

    await state.update_data(transaction_description=message.text)
    await message.answer("🎉 Описание добавлено! Теперь укажите сумму транзакции:")
    await state.set_state(TransactionStates.waiting_for_transaction_amount)