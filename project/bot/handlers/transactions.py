from aiogram import Router, F
from aiogram.filters import or_f,StateFilter
from aiogram.types import Message, CallbackQuery
from project.bot.messages.messages import *
from aiogram.fsm.context import FSMContext
from project.bot.states import *
from project.bot.keyboards.reply import *
from project.bot.Save import save
router=Router()

@router.message(or_f(F.text == "Добaвить транзакцию"))
async def add_transaction_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        open("add_handler.txt", "w").write(str(await save.update(user_id, "ADD_TRANSACTION")))
        open("main44.txt", "w").write(str(await save.convert_to_json()))
        await message.answer("В скорых обновлениях")
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(F.text == "Пропустить", TransactionStates.waiting_for_transaction_description)
async def handle_skip_description(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("skip_desc.txt", "w").write(str(await save.update(user_id, "SKIP_TRANSACTIONS")))
    try:
        await state.update_data(transaction_description=None)
        await message.answer("🎉 Укажите сумму транзакции:")
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
    except Exception as e:
        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")

#@router.message(F.text == "Посмотреть список записей")
#async def show_transactions_list(message:Message, state:FSMContext):
#    user_id=Message.from_user.id
#    await save.update(user_id,"LIST_TRANSACTIONS")
#    try:
#        await
#    except Exception as e:
#        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")

@router.message(TransactionStates.waiting_for_transaction_description)
async def handle_description_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("desc_input.txt", "w").write(str(await save.update(user_id, "NOT_SKIP_TRANSACTIONS")))
    try:
        await state.update_data(transaction_description=message.text)
        await message.answer("🎉 Описание добавлено! Теперь укажите сумму транзакции:")
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
    except Exception as e:
        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")