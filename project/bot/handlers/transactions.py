from aiogram import Router, F
import re
from aiogram.filters import or_f,StateFilter
from aiogram.types import Message, CallbackQuery
from project.bot.messages.messages import *
from aiogram.fsm.context import FSMContext
from project.bot.states import *
from project.bot.keyboards.reply import *
from project.bot.Save import save
from datetime import datetime
import calendar
router=Router()
abb=["1","2","3","4","5","6","7","8"]
def is_valid_string(s):
    # Проверяем, содержит ли строка что-либо кроме цифр
    if re.search(r'[^\d]', s):
        # Проверяем конкретные запрещенные категории
        if re.search(r'[а-яА-Яa-zA-Z]', s):  # Буквы
            return False, "Строка содержит буквы"
        if re.search(r'[@#$%^&*()_+=\[\]{};:\'",<>/?\\|`~]', s):  # Спецсимволы
            return False, "Строка содержит специальные символы"
        if ' ' in s:  # Пробелы
            return False, "Строка содержит пробелы"
        if re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0]', s):
            return False, "Строка содержит смайлики или другие значки"
        return False, "Строка содержит недопустимые символы"
    return True, "Строка валидна"

@router.message(F.text == "Добaвить запись")
async def add_transaction(message: Message, state: FSMContext):
    try:
        await message.answer(
            add_trans
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(F.text.in_(abb))
async def add_after_transaction(message: Message, state: FSMContext):
    try:
        await message.answer(
            "📝 Введите описание для вашей записи (или пропустите):",
            reply_markup=await zapis_add()
        )
        await state.set_state(TransactionStates.waiting_for_transaction_description)
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(TransactionStates.waiting_for_transaction_description)
async def after_name(message: Message, state: FSMContext):
    name = message.text.strip()
    try:
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
        await message.answer(
            "🎉Укажите теперь сумму вашей записи:",

        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(F.text=="Пропустить описание")
async def after_description(message: Message, state: FSMContext):
    try:
        await message.answer(
            "🎉Укажите теперь сумму вашей записи:"
        )
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(TransactionStates.waiting_for_transaction_amount)
async def after_amount(message: Message, state: FSMContext):
    name = message.text.strip()
    try:
        if(is_valid_string(name)==False):
            await message.answer(
                text_no,
                )
            return
        else:
            await state.set_state(TransactionStates.wait_date)
            await message.answer(
                "Ура! 🎉 Ты успешно добавил сумму! Теперь укажи дату 📅😊",
                reply_markup=await doty_keyboard(),
                )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")
        
@router.message(TransactionStates.wait_date)
async def after_date(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
        await message.answer(
            "🎉 Отлично! Я сохранил вашу запись😊\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")









@router.message(F.text == "Изменить запись")
async def update_transaction_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        open("add_handler.txt", "w").write(str(await save.update(user_id, "ADD_TRANSACTION")))
        open("main44.txt", "w").write(str(await save.convert_to_json()))
        await message.answer("В скорых обновлениях")
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(F.text == "Удалить запись")
async def del_transaction_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        open("add_handler.txt", "w").write(str(await save.update(user_id, "ADD_TRANSACTION")))
        open("main44.txt", "w").write(str(await save.convert_to_json()))
        await message.answer("В скорых обновлениях")
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")


#@router.message(F.text == "История моих записей")
#async def show_transactions_list(message:Message, state:FSMContext):
#    user_id=Message.from_user.id
#    await save.update(user_id,"LIST_TRANSACTIONS")
#    try:
#        await
#    except Exception as e:
#        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")
