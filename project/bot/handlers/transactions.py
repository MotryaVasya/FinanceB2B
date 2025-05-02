from aiogram import Router, F
from aiogram.filters import or_f, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from project.bot.Save import save
from project.bot.conecting_methods.transactions import delete_transaction, get_transactions
from project.bot.messages.mesage_transaction import PAGE_SIZE, get_paginated_transactions
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

# Define states for FSM
class TransactionStates(StatesGroup):
    in_add = State()
    waiting_for_transaction_description = State()
    waiting_for_transaction_amount = State()
    wait_date = State()
    in_update_name = State()
    in_update_cat = State()
    update_for_transaction_description = State()
    update_for_transaction_amount = State()
    wait_date_update = State()
    update_no_sets = State()
    in_delete = State() # Not used, but good to have for consistency

# Global variables (it's generally better to manage state within the bot's FSM)
user_pages = {}
add_trans = "Add transaction details."
text_no = "Invalid input. Please enter a valid number."
avtobus = ["", "", "", ""]


async def check_action(action: str, total_pages: int, current_page: int, callback: CallbackQuery | None = None,
                       state: FSMContext | None = None, for_update: bool = False,
                       for_delete: bool = False, all_transactions: list | None = None,
                       user_id: int | None = None) -> int | None:
    """
    Helper function to determine the new page based on the action.

    Args:
        action: The action from the callback data.
        total_pages: The total number of pages.
        current_page: The current page number.
        callback: The callback query.
        state: The FSM context.
        for_update: Flag for update operation.
        for_delete: Flag for delete operation.
        all_transactions: List of all transactions.
        user_id: User ID.

    Returns:
        The new page number, or None if the action is invalid.
    """
    if action == "next":
        return min(current_page + 1, total_pages - 1)
    elif action == "prev":
        return max(current_page - 1, 0)
    elif action == "first":
        return 0
    elif action == "last":
        return total_pages - 1
    elif action == "back5":
        return max(current_page - 5, 0)
    elif action == "forward5":
        return min(current_page + 5, total_pages - 1)
    elif action == "choose":  # Add handling for "choose" action
        if for_update:
            if callback and user_id is not None:
                keyboard = await choose_buttons_update(user_id, all_transactions[current_page * PAGE_SIZE: (current_page + 1) * PAGE_SIZE])
                await callback.message.edit_text("Select a transaction to update:", reply_markup=keyboard)
                return None
        elif for_delete:
            if callback and user_id is not None:
                keyboard = await choose_buttons_delete(user_id, all_transactions[current_page * PAGE_SIZE: (current_page + 1) * PAGE_SIZE])
                await callback.message.edit_text("Select a transaction to delete:", reply_markup=keyboard)
                return None
        else:
            return current_page
    return current_page  # default


@router.message(or_f(F.text == "Добaвить запись"))
async def add_transaction_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("show_categories.txt", "w").write(str(await save.update(user_id, "ADD_TRANSACTION")))
    try:
        await state.set_state(TransactionStates.in_add)
        await message.answer(
            reply_markup=ReplyKeyboardRemove(),  # Use ReplyKeyboardRemove()
            text=add_trans
        )
    except Exception as e:
        logger.error(f"Error adding transaction: {e}", exc_info=True)


@router.message(StateFilter(TransactionStates.in_add))
async def add_after_transaction(message: Message, state: FSMContext):
    try:
        await message.answer(
            "📝 Введите описание для вашей записи (или пропустите):",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Пропустить описание"]], resize_keyboard=True)
        )
        await state.set_state(TransactionStates.waiting_for_transaction_description)
    except Exception as e:
        logger.error(f"Error after transaction: {e}", exc_info=True)


@router.message(F.text == "Пропустить описание")
async def after_description(message: Message, state: FSMContext):
    try:
        await message.answer(
            "🎉Укажите теперь сумму вашей записи:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
    except Exception as e:
        logger.error(f"Error after description: {e}", exc_info=True)



@router.message(TransactionStates.waiting_for_transaction_description)
async def after_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("show_categories.txt", "w").write(str(await save.update(user_id, "SUM_DESCRIPTION")))
    try:
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
        await message.answer(
            "🎉Укажите теперь сумму вашей записи:",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Error after name: {e}", exc_info=True)



@router.message(TransactionStates.waiting_for_transaction_amount)
async def after_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("show_categories.txt", "w").write(str(await save.update(user_id, "TRANSACTION_DESCRIPTION_DATA")))
    try:
        if message.text.isdigit():
            await state.set_state(TransactionStates.wait_date)
            await message.answer(
                "Ура! 🎉 Ты успешно добавил сумму! Теперь укажи дату 📅😊",
                reply_markup=ReplyKeyboardMarkup(keyboard=[["Сегодня", "Вчера"], ["Другая дата"]], resize_keyboard=True),
            )
        else:
            await message.answer(
                text_no,
            )
            return

    except Exception as e:
        logger.error(f"Error after amount: {e}", exc_info=True)



@router.message(TransactionStates.wait_date)
async def after_date(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
        await message.answer(
            "🎉 Отлично! Я сохранил вашу запись😊\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Добaвить запись", "Изменить запись"], ["Удалить запись", "История моих записей"]], resize_keyboard=True)
        )
    except Exception as e:
        logger.error(f"Error after date: {e}", exc_info=True)



@router.message(or_f(F.text == "Изменить запись", F.text == "Пропустить изменение категории"))
async def update_transaction_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_pages[user_id] = 0
    try:
        await state.set_state(TransactionStates.in_update_name)
        open("add_handler.txt", "w").write(str(await save.update(user_id, "ADD_TRANSACTION")))
        open("main44.txt", "w").write(str(await save.convert_to_json()))

        transactions = await get_transactions(user_id)
        total_pages = (len(transactions) + PAGE_SIZE - 1) // PAGE_SIZE
        message_text, _ = await get_paginated_transactions(user_id, 0)
        keyboard = await build_pagination_keyboard_for_update(0, total_pages, user_id)

        await message.answer(
            "🎉 Вот все ваши записи! Какую вы хотите изменить?\n\n" + message_text,
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Error showing transactions for update: {e}", exc_info=True)



@router.callback_query(F.data.startswith("transactionU_"))
async def handle_pagination_for_update(callback: CallbackQuery, state: FSMContext):
    try:
        data_parts = callback.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        current_page = user_pages.get(user_id, 0)
        all_transactions = await get_transactions(user_id)
        total_pages = (len(all_transactions) + PAGE_SIZE - 1) // PAGE_SIZE

        new_page = await check_action(
            action=action,
            total_pages=total_pages,
            current_page=current_page,
            callback=callback,
            state=state,
            for_update=True,
            all_transactions=all_transactions,
            user_id=user_id
        )
        if new_page is None:
            return

        user_pages[user_id] = new_page
        message_text, _ = await get_paginated_transactions(user_id, new_page)
        keyboard = await build_pagination_keyboard_for_update(new_page, total_pages, user_id)

        await callback.message.edit_text(text=message_text, reply_markup=keyboard)
        await callback.answer()

    except Exception as e:
        logger.error(f"Pagination error during update: {e}", exc_info=True)
        await callback.answer("Произошла ошибка, попробуйте позже")



@router.callback_query(F.data.startswith("select_transactionU_"))
async def handle_transaction_selection_for_update(callback: CallbackQuery, state: FSMContext):
    transaction_id = int(callback.data.split('_')[2])
    transaction_name = str(callback.data.split('_')[3])
    await state.update_data(selected_transaction_id=transaction_id)
    await state.update_data(selected_transaction_name=transaction_name)

    await state.set_state(TransactionStates.in_update_cat)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Пропустить", callback_data="skip_update_cat"))
    await callback.message.edit_text(
        text=f"Выбрана транзакция для изменения: '{transaction_name}'.\n\n"
             "✨ Выберите новую категорию, пожалуйста!\n"
             "1. название\n"
             "2. название\n"
             "итп.\n",
        reply_markup=builder.as_markup()
    )
    await callback.answer()



@router.message(TransactionStates.in_update_cat)
async def del_after_choos2(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.update_for_transaction_description)
        await message.answer(
            "📝 Введите описание для вашей записи (или пропустите):\n",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Пропустить описание записи"]], resize_keyboard=True)
        )
    except Exception as e:
        logger.error(f"Error in del_after_choos2: {e}", exc_info=True)


@router.message(F.text == "Пропустить описание записи")
async def del_after_choos3(message: Message, state: FSMContext):
    try:
        global avtobus
        avtobus[0] = message.text.strip()
        await state.set_state(TransactionStates.update_for_transaction_amount)
        await message.answer(
            "🎉Измените сумму вашей записи:\n",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Пропустить изменение суммы"]], resize_keyboard=True)
        )
    except Exception as e:
        logger.error(f"Error in del_after_choos3: {e}", exc_info=True)


@router.message(TransactionStates.update_for_transaction_description)
async def del_after_choos4(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.update_for_transaction_amount)
        await message.answer(
            "🎉Измените сумму вашей записи:\n",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Пропустить изменение суммы"]], resize_keyboard=True)
        )
    except Exception as e:
        logger.error(f"Error in del_after_choos4: {e}", exc_info=True)


@router.message(F.text == "Пропустить изменение суммы")
async def del_after_choos5(message: Message, state: FSMContext):
    try:
        global avtobus
        avtobus[1] = message.text.strip()
        await state.set_state(TransactionStates.wait_date_update)
        await message.answer(
            "Ура!Теперь измени дату 📅😊\n",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Пропустить изменение даты", "Другая дата"]], resize_keyboard=True)
        )
    except Exception as e:
        logger.error(f"Error in del_after_choos5: {e}", exc_info=True)



@router.message(TransactionStates.update_for_transaction_amount)
async def del_after_choos6(message: Message, state: FSMContext):
    try:
        if message.text.isdigit():
            await state.set_state(TransactionStates.wait_date_update)
            await message.answer(
                "Ура! 🎉 Ты успешно добавил сумму! Теперь измени дату 📅😊\n",
                reply_markup=ReplyKeyboardMarkup(keyboard=[["Пропустить изменение даты", "Другая дата"]], resize_keyboard=True)
            )
        else:
            await message.answer(
                text_no
            )
            return
    except Exception as e:
        logger.error(f"Error in del_after_choos6: {e}", exc_info=True)



@router.message(or_f(TransactionStates.wait_date_update, F.text == "Пропустить изменение даты"))
async def after_date_update(message: Message, state: FSMContext):
    global avtobus
    avtobus[2] = message.text.strip()
    try:
        if all(v == "Пропустить описание записи" or v == "Пропустить изменение суммы" or v == "Пропустить изменение даты" for v in avtobus[:3]):
            await state.set_state(TransactionStates.update_no_sets)
            await message.answer(
                "😕 Ничего не изменилось.\n Хотите вернуться и попробовать снова или оставить всё как есть?\n",
                reply_markup=ReplyKeyboardMarkup(keyboard=[["Попробовать снова", "Оставить как есть"]], resize_keyboard=True)
            )
        else:
            await state.clear()
            await message.answer(
                "🎉 Отлично! Я сохранил вашу запись😊\n"
                "🔙 Возвращаемся в главное меню!\n",
                reply_markup=ReplyKeyboardMarkup(keyboard=[["Добaвить запись", "Изменить запись"], ["Удалить запись", "История моих записей"]], resize_keyboard=True)
            )
    except Exception as e:
        logger.error(f"Error after date update: {e}", exc_info=True)



@router.message(or_f(StateFilter(TransactionStates.update_no_sets), F.text == "Оставить как есть"))
async def set_type(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer(
            "👌 Всё оставлено как есть! Если что-то нужно будет изменить, я всегда готов помочь 😊\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Добaвить запись", "Изменить запись"], ["Удалить запись", "История моих записей"]], resize_keyboard=True)
        )
    except Exception as e:
        logger.error(f"Error in set_type: {e}", exc_info=True)



@router.message(F.text == 'Удалить запись')
async def delete_transaction_message(message: Message, state: FSMContext):
    await handle_delete_flow(message.from_user.id, message, state)


@router.callback_query(F.data == 'back_to_list_transactions')
async def back_to_list_callback(callback: CallbackQuery, state: FSMContext):
    await handle_delete_flow(callback.from_user.id, callback.message, state)



async def handle_delete_flow(user_id: int, message: Message, state: FSMContext):
    user_pages[user_id] = 0

    try:
        message_text, total_pages = await get_paginated_transactions(user_id, 0)
        keyboard = await build_pagination_keyboard_for_delete(0, total_pages, user_id)
        await message.answer('🙂 Вот список ваших записей! Какую из них хотите удалить?\n\n' + message_text,
                            reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in handle_delete_flow: {e}", exc_info=True)



@router.callback_query(F.data.startswith("transactionD_"))
async def handle_pagination_for_delete(callback: CallbackQuery, state: FSMContext):
    try:
        data_parts = callback.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        current_page = user_pages.get(user_id, 0)
        all_transactions = await get_transactions(user_id)
        total_pages = (len(all_transactions) + PAGE_SIZE - 1) // PAGE_SIZE

        new_page = await check_action(
            action=action,
            total_pages=total_pages,
            current_page=current_page,
            callback=callback,
            state=state,
            for_delete=True,
            all_transactions=all_transactions,
            user_id=user_id
        )
        if new_page is None:
            return

        user_pages[user_id] = new_page
        message_text, total_pages = await get_paginated_transactions(user_id, new_page)
        keyboard = await build_pagination_keyboard_for_delete(new_page, total_pages, user_id)

        await callback.message.edit_text(text=message_text, reply_markup=keyboard)
        await callback.answer()

    except Exception as e:
        logger.error(f"Pagination error in delete: {e}", exc_info=True)
        await callback.answer("Произошла ошибка, попробуйте позже")



@router.callback_query(F.data.startswith("select_transactionD_"))
async def handle_transaction_selection_for_delete(callback: CallbackQuery, state: FSMContext):
    transaction_id = int(callback.data.split('_')[2])
    transaction_name = str(callback.data.split('_')[3])
    await state.update_data(selected_transaction_id=transaction_id)
    await state.update_data(selected_transaction_name=transaction_name)

    # Получаем оригинальное сообщение
    data = await state.get_data()
    original_message = data.get('original_message', "Список транзакций")

    # Создание клавиатуры через билдер
    builder = await confirm_or_cancel_buttons() # confirm_or_cancel_buttons returns InlineKeyboardMarkup

    await callback.message.edit_text(
        text=f"{original_message}\n\n"
             f"Выбрана транзакция : '{transaction_name}'\n"
             f"❗️Вы уверены, что хотите удалить эту запись?",
        reply_markup=builder # Removed .as_markup()
    )
    await callback.answer()



@router.callback_query(F.data == "confirm_delete")
async def confirm_delete_transaction(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    transaction_id = data.get("selected_transaction_id")
    transaction_name = data.get("selected_transaction_name")

    if transaction_id is not None:
        res = await delete_transaction(transaction_id)
        if res:
            await callback.message.answer(
                text=f"🗑 Готово! Ваша запись успешно удалена 😊\n🔙 Возвращаемся в главное меню!",
                reply_markup=ReplyKeyboardMarkup(keyboard=[["Добaвить запись", "Изменить запись"], ["Удалить запись", "История моих записей"]], resize_keyboard=True)
            )

    else:
        await callback.message.edit_text("⚠️ Ошибка: ID транзакции не найден.")

    await callback.answer()
    await state.clear()



@router.callback_query(F.data == "cancel_delete")
async def cancel_delete_transaction(callback: CallbackQuery, state: FSMContext):
    builder = await back_menu_or_list_transactions()
    await callback.message.answer("🙂 Хотите удалить другую запись или вернуться в главное меню?",
                                 reply_markup=builder.as_markup())
    await state.clear()



@router.message(F.text == 'История моих записей')
async def show_transactions(message: Message):
    user_id = message.from_user.id
    user_pages[user_id] = 0  # Сбрасываем на первую страницу

    try:
        message_text, total_pages = await get_paginated_transactions(user_id, 0)
        keyboard = await build_pagination_keyboard_for_show(0, total_pages, user_id)
        await message.answer('📂 Вот список всех записей😊 :\n\n' + message_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error showing transactions: {e}", exc_info=True)



@router.callback_query(F.data.startswith("transactions_"))
async def handle_pagination_for_show(callback: CallbackQuery):
    try:
        data_parts = callback.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        current_page = user_pages.get(user_id, 0)
        all_transactions = await get_transactions(user_id)
        total_pages = (len(all_transactions) + PAGE_SIZE - 1) // PAGE_SIZE

        # Определяем новую страницу
        new_page = await check_action(action=action, total_pages=total_pages, current_page=current_page, callback=callback)

        user_pages[user_id] = new_page
        message_text, total_pages = await get_paginated_transactions(user_id, new_page)
        keyboard = await build_pagination_keyboard_for_show(new_page, total_pages, user_id)

        await callback.message.edit_text(message_text, reply_markup=keyboard)
        await callback.answer()

    except Exception as e:
        logger.error(f"Pagination error in show: {e}", exc_info=True)
        await callback.answer(f"Произошла ошибка, попробуйте позже")



async def build_pagination_keyboard_for_show(page: int, total_pages: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Основные кнопки навигации
    if page > 0:
        builder.add(InlineKeyboardButton(text="<", callback_data=f"transactions_prev_{user_id}"))  # На 1 назад

    if page < total_pages - 1:
        builder.add(InlineKeyboardButton(text=">",callback_data=f"transactions_next_{user_id}"))  # На 1 вперед

    if page >= 1:  # Если не на первой странице
        if page >= 5:
            builder.add(InlineKeyboardButton(text="<<", callback_data=f"transactions_back5_{user_id}"))  # На 5 назад
        else:
            builder.add(InlineKeyboardButton(text="<<", callback_data=f"transactions_first_{user_id}"))  # В начало

    if page < total_pages - 1:  # Если не на последней странице
        if page + 5 < total_pages:
            builder.add(InlineKeyboardButton(text=">>", callback_data=f"transactions_forward5_{user_id}"))  # На 5 вперед
        else:
            builder.add(InlineKeyboardButton(text=">>", callback_data=f"transactions_last_{user_id}"))  # В конец

    builder.adjust(2, 2)
    return builder.as_markup()



async def build_pagination_keyboard_for_update(page: int, total_pages: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Основные кнопки навигации
    if page > 0:
        builder.add(InlineKeyboardButton(text="<", callback_data=f"transactionU_prev_{user_id}"))  # На 1 назад

    builder.add(InlineKeyboardButton(text="Выбрать страницу", callback_data=f"transactionU_choose_{user_id}"))

    if page < total_pages - 1:
        builder.add(InlineKeyboardButton(text=">", callback_data=f"transactionU_next_{user_id}"))  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if page >= 1:  # Если не на первой странице
        if page >= 5:
            builder.add(InlineKeyboardButton(text="<<", callback_data=f"transactionU_back5_{user_id}"))  # На 5 назад
        else:
            builder.add(InlineKeyboardButton(text="<<", callback_data=f"transactionU_first_{user_id}"))  # В начало

    if page < total_pages - 1:  # Если не на последней странице
        if page + 5 < total_pages:
            builder.add(InlineKeyboardButton(text=">>", callback_data=f"transactionU_forward5_{user_id}"))  # На 5 вперед
        else:
            builder.add(InlineKeyboardButton(text=">>", callback_data=f"transactionU_last_{user_id}"))  # В конец

    builder.adjust(3, 2)
    return builder.as_markup()



async def build_pagination_keyboard_for_update_categories(page: int, total_pages: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Основные кнопки навигации
    if page > 0:
        builder.add(InlineKeyboardButton(text="<", callback_data=f"transactionUC_prev_{user_id}"))  # На 1 назад

    builder.add(InlineKeyboardButton(text="Выбрать страницу", callback_data=f"transactionUC_choose_{user_id}"))

    if page < total_pages - 1:
        builder.add(InlineKeyboardButton(text=">", callback_data=f"transactionUC_next_{user_id}"))  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if page >= 1:  # Если не на первой странице
        if page >= 5:
            builder.add(InlineKeyboardButton(text="<<", callback_data=f"transactionUC_back5_{user_id}"))  # На 5 назад
        else:
            builder.add(InlineKeyboardButton(text="<<", callback_data=f"transactionUC_first_{user_id}"))  # В начало

    if page < total_pages - 1:  # Если не на последней странице
        if page + 5 < total_pages:
            builder.add(InlineKeyboardButton(text=">>", callback_data=f"transactionUC_forward5_{user_id}"))  # На 5 вперед
        else:
            builder.add(InlineKeyboardButton(text=">>", callback_data=f"transactionUC_last_{user_id}"))  # В конец

    builder.adjust(3, 2)
    return builder.as_markup()



async def build_pagination_keyboard_for_delete(page: int, total_pages: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Основные кнопки навигации
    if page > 0:
        builder.add(InlineKeyboardButton(text="<", callback_data=f"transactionD_prev_{user_id}"))  # На 1 назад

    builder.add(InlineKeyboardButton(text="Выбрать страницу", callback_data=f"transactionD_choose_{user_id}"))

    if page < total_pages - 1:
        builder.add(InlineKeyboardButton(text=">", callback_data=f"transactionD_next_{user_id}"))  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if page >= 1:  # Если не на первой странице
        if page >= 5:
            builder.add(InlineKeyboardButton(text="<<", callback_data=f"transactionD_back5_{user_id}"))  # На 5 назад
        else:
            builder.add(InlineKeyboardButton(text="<<", callback_data=f"transactionD_first_{user_id}"))  # В начало

    if page < total_pages - 1:  # Если не на последней странице
        if page + 5 < total_pages:
            builder.add(InlineKeyboardButton(text=">>", callback_data=f"transactionD_forward5_{user_id}"))  # На 5 вперед
        else:
            builder.add(InlineKeyboardButton(text=">>", callback_data=f"transactionD_last_{user_id}"))  # В конец

    builder.adjust(3, 2)
    return builder.as_markup()



async def choose_buttons_delete(user_id: int, page_transactions: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tx in page_transactions:
        tx_text = f"🔖 {tx['category_name']} | {tx['full_sum']:.2f} ₽ | 📅 {tx['date'][:10]}"
        builder.add(InlineKeyboardButton(text=tx_text, callback_data=f"select_transactionD_{tx['id']}_{tx['description']}"))

    builder.add(InlineKeyboardButton(text="◀ Назад", callback_data=f"transactionD_back_{user_id}"))
    builder.adjust(1)
    return builder.as_markup()



async def choose_buttons_update(user_id: int, page_transactions: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tx in page_transactions:
        tx_text = f"🔖 {tx['category_name']} | {tx['full_sum']:.2f} ₽ | 📅 {tx['date'][:10]}"
        builder.add(InlineKeyboardButton(text=tx_text, callback_data=f"select_transactionU_{tx['id']}_{tx['description']}"))

    builder.add(InlineKeyboardButton(text="◀ Назад", callback_data=f"transactionU_back_{user_id}"))
    builder.adjust(1)
    return builder.as_markup()



async def confirm_or_cancel_buttons() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_delete"))
    builder.add(InlineKeyboardButton(text="❌ Нет", callback_data="cancel_delete"))
    builder.adjust(2)
    return builder.as_markup()



async def back_menu_or_list_transactions() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Вернутся к списку ваших записей', callback_data='back_to_list_transactions'))
    builder.add(InlineKeyboardButton(text='Вернутся к меню', callback_data='back_to_menu'))
    return builder.as_markup()



async def retry_or_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для повторной попытки или отмены"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="retry_update"))
    builder.add(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_update"))
    return builder.as_markup()



async def confirm_changes_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения изменений"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_changes"))
    builder.add(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_update"))
    return builder.as_markup()
