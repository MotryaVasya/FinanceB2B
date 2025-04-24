from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from project.bot.messages.messages import *
from aiogram.fsm.context import FSMContext
from project.bot.states import *
from project.bot.keyboards.reply import *
router=Router()


@router.callback_query(F.text == "Добавить")
async def alert(callback: CallbackQuery):
    await callback.answer(text='В скором будущем', show_alert=True)

#TODO доделать добавление, удаление, обновление
@router.message(F.text == "Добавить")
async def add_handler(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        await check_states_add(current_state, message)
        await message.answer(text=create_transaction_text)
    except Exception as e:
        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")


@router.message(F.text == "Пропустить", TransactionStates.waiting_for_transaction_description)
async def handle_skip_description(message: Message, state: FSMContext):
    
    await state.update_data(transaction_description=None)
    await message.answer("🎉 Укажите сумму вашей записи:")
    await state.set_state(TransactionStates.waiting_for_transaction_amount)


@router.message(TransactionStates.waiting_for_transaction_description)
async def handle_description_input(message: Message, state: FSMContext):

    await state.update_data(transaction_description=message.text)
    await message.answer("🎉 Описание добавлено! Теперь укажите сумму вашей записи:")
    await state.set_state(TransactionStates.waiting_for_transaction_amount)