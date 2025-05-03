from typing import Union
from aiogram import Router, F
import re
from aiogram.filters import or_f,StateFilter,and_f
from aiogram.types import Message, CallbackQuery,ReplyKeyboardRemove
from project.bot.conecting_methods.category import get_categories
from project.bot.conecting_methods.methods import check_action
from project.bot.messages.messages import *
from aiogram.fsm.context import FSMContext
from project.bot.states import *
from project.bot.keyboards.reply import *
from project.bot.Save import save
from datetime import datetime
import calendar
import math
from project.bot.keyboards.inline_transactions import build_category_choice_keyboard, build_pagination_keyboard_for_categories
from project.bot.conecting_methods.transactions import create_transaction, delete_transaction, get_transactions,update_transaction,get_transaction
from project.bot.messages.mesage_transaction import PAGE_SIZE, get_paginated_transactions
from project.bot.keyboards.inline_transactions import (back_menu_or_list_transactions,
                                                       build_pagination_keyboard_for_delete,choose_buttons_update,build_pagination_keyboard_for_update ,build_pagination_keyboard_for_show, confirm_or_cancel_buttons)
from project.bot.messages.mesage_transaction import user_pages

router=Router()
abb=["1","2","3","4","5","6","7","8"]
abo=["1","2"]
avtobus=["","","",""]


class AddTransaction(StatesGroup):
    waiting_for_category = State()
    waiting_for_amount = State()
    waiting_for_description = State()
    waiting_for_date = State()
    waiting_for_confirmation = State()

@router.message(F.text == 'add transaction')
async def add_transaction_start(message: Message, state: FSMContext):
    # Получаем список категорий пользователя
    categories = await get_categories(message.from_user.id)

    if not categories:
        await message.answer("У вас нет категорий. Сначала создайте хотя бы одну категорию.")
        return

    await state.update_data(all_categories=categories)
    user_pages[message.from_user.id] = 0

    try:
        message_text = await format_categories_page(categories, 0)
        total_pages = max(1, (len(categories) + PAGE_SIZE - 1) // PAGE_SIZE)
        keyboard = await build_pagination_keyboard_for_categories(0, total_pages, message.from_user.id)

        await state.set_state(AddTransaction.waiting_for_category)
        await message.answer(
            "Выберите категорию для новой транзакции:\n\n" + message_text,
            reply_markup=keyboard
        )
    except Exception as e:
        await message.answer(f"Ошибка при получении категорий: {e}")
async def format_categories_page(categories: list, page: int) -> str:
    """Форматирует страницу с категориями для отображения"""
    start_idx = page * PAGE_SIZE
    page_categories = categories[start_idx:start_idx + PAGE_SIZE]

    formatted = []
    for cat in page_categories:
        try:
            name = cat['name_category'].encode('utf-8').decode('utf-8')
        except:
            name = cat['name_category']

        cat_type = 'Доход' if cat['type'] == 1 else 'Расход'
        formatted.append(
            f"🔖 {name}\n"
            f"📝 Тип: {cat_type}\n"
            f"━━━━━━━━━━━━━━━━━"
        )

    total_pages = max(1, (len(categories) + PAGE_SIZE - 1) // PAGE_SIZE)
    header = "Список категорий:\n\n"
    message = header + "\n\n".join(formatted)
    message += f"\n\nСтраница {page + 1}/{total_pages}"

    return message

@router.callback_query(F.data.startswith("tx_categories_"), AddTransaction.waiting_for_category)
async def handle_pagination_for_categories(callback: CallbackQuery, state: FSMContext):
    try:
        data_parts = callback.data.split('_')
        action = data_parts[2]
        user_id = int(data_parts[3])
        current_page = user_pages.get(user_id, 0)

        state_data = await state.get_data()
        categories = state_data.get('all_categories', [])
        total_pages = max(1, (len(categories) + PAGE_SIZE - 1) // PAGE_SIZE)

        if action == "choose":
            start_idx = current_page * PAGE_SIZE
            page_categories = categories[start_idx:start_idx + PAGE_SIZE]
            keyboard = await build_category_choice_keyboard(page_categories, user_id)
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await callback.answer()
            return

        elif action == "back":
            message_text = await format_categories_page(categories, current_page)
            keyboard = await build_pagination_keyboard_for_categories(current_page, total_pages, user_id)
            await callback.message.edit_text(
                text="Выберите категорию для новой транзакции:\n\n" + message_text,
                reply_markup=keyboard
            )
            await callback.answer()
            return

        # Обработка пагинации
        new_page = current_page
        if action == "prev":
            new_page = max(0, current_page - 1)
        elif action == "next":
            new_page = min(total_pages - 1, current_page + 1)
        elif action == "back5":
            new_page = max(0, current_page - 5)  # На 5 страниц назад (но не меньше 0)
        elif action == "forward5":
            new_page = min(total_pages - 1, current_page + 5)  # На 5 страниц вперед (но не больше максимума)
        elif action == "first":
            new_page = 0
        elif action == "last":
            new_page = total_pages - 1

        if new_page != current_page:
            user_pages[user_id] = new_page
            message_text = await format_categories_page(categories, new_page)
            keyboard = await build_pagination_keyboard_for_categories(new_page, total_pages, user_id)
            await callback.message.edit_text(
                text="Выберите категорию для новой транзакции:\n\n" + message_text,
                reply_markup=keyboard
            )

        await callback.answer()

    except Exception as e:
        print(f"Error in handle_pagination_for_categories: {e}")
        await callback.answer("Произошла ошибка при обработке")
@router.callback_query(F.data.startswith("addtx_category_"))
async def add_transaction_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[2])
    await state.update_data(category_id=category_id)
    await state.set_state(AddTransaction.waiting_for_amount)

    # Получаем данные о категории для отображения
    categories = await get_categories(callback.from_user.id)
    category = next((c for c in categories if c['id'] == category_id), None)

    if category:
        await state.update_data(category_name=category['name_category'])
        await callback.message.edit_text(
            f"Категория: {category['name_category']}\n\n"
            "Введите сумму транзакции (например: 1000 или 150.50):",
            reply_markup=None
        )
    else:
        await callback.message.edit_text("Ошибка: категория не найдена")
        await state.clear()

    await callback.answer()

@router.message(AddTransaction.waiting_for_amount)
async def add_transaction_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля")

        await state.update_data(amount=amount)
        await state.set_state(AddTransaction.waiting_for_description)

        builder = InlineKeyboardBuilder()
        builder.button(text="Пропустить", callback_data="addtx_skip_description")
        builder.button(text="❌ Отмена", callback_data="addtx_cancel")
        builder.adjust(2)

        await message.answer(
            f"Сумма: {amount:.2f} ₽\n\n"
            "Введите описание транзакции (или нажмите 'Пропустить'):",
            reply_markup=builder.as_markup()
        )
    except ValueError:
        await message.answer("Некорректная сумма. Введите число (например: 1000 или 150.50):")

@router.callback_query(F.data == "addtx_skip_description")
async def skip_description(callback: CallbackQuery, state: FSMContext):
    await state.update_data(description=None)
    await state.set_state(AddTransaction.waiting_for_date)
    builder = InlineKeyboardBuilder()
    builder.button(text="Сегодня", callback_data="addtx_date_today")
    builder.button(text="Ввести дату", callback_data="addtx_date_custom")
    builder.adjust(2)
    await callback.message.edit_text(
        "Описание: не указано\n\n"
        "Выберите дату транзакции:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.message(AddTransaction.waiting_for_description)
async def add_transaction_description(message: Message, state: FSMContext):
    description = message.text.strip()
    await state.update_data(description=description)
    await state.set_state(AddTransaction.waiting_for_date)

    builder = InlineKeyboardBuilder()
    builder.button(text="Сегодня", callback_data="addtx_date_today")
    builder.button(text="Ввести дату", callback_data="addtx_date_custom")
    builder.adjust(2)

    await message.answer(
        f"Описание: {description}\n\n"
        "Выберите дату транзакции:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data == "addtx_date_today")
async def set_date_today(callback: CallbackQuery, state: FSMContext):
    today = datetime.now().strftime("%Y-%m-%d")
    await state.update_data(date=today)
    await show_confirmation(callback, state)
    await callback.answer()

@router.callback_query(F.data == "addtx_date_custom")
async def ask_custom_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите дату в формате ГГГГ-ММ-ДД (например: 2023-12-31):",
        reply_markup=None
    )
    await callback.answer()
@router.callback_query(F.data.startswith("calendar_"))
async def handle_calendar_actions(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    if action == "day":
        # Обработка выбора дня
        _, _, year, month, day = callback.data.split("_")
        selected_date = f"{year}-{month}-{day}"


        if int(day) < 10:
            selected_date = f"{year}-{month}-0{day}"
        if int(month) < 10:
            selected_date = f"{year}-0{month}-{day}"
        if int(month) < 10 and int(day) < 10:
            selected_date = f"{year}-0{month}-0{day}"

        await state.update_data(date=selected_date)
        await show_confirmation(callback, state)

    elif action == "prev":
        # Переход к предыдущему месяцу
        _, _, year, month = callback.data.split("_")
        year, month = int(year), int(month)
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        keyboard = generate_calendar(year, month)
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    elif action == "next":
        # Переход к следующему месяцу
        _, _, year, month = callback.data.split("_")
        year, month = int(year), int(month)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        keyboard = generate_calendar(year, month)
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    elif action == "confirm":
        # Подтверждение выбранной даты
        data = await state.get_data()
        if 'date' not in data:
            await callback.answer("Сначала выберите дату", show_alert=True)
            return
        await show_confirmation(callback, state)

    elif action == "cancel":
        # Отмена выбора даты
        await state.set_state(AddTransaction.waiting_for_date)
        builder = InlineKeyboardBuilder()
        builder.button(text="Сегодня", callback_data="addtx_date_today")
        builder.button(text="Ввести дату", callback_data="addtx_date_custom")
        builder.adjust(2)
        await callback.message.edit_text(
            "Выберите дату транзакции:",
            reply_markup=builder.as_markup()
        )

    await callback.answer()

async def show_confirmation(update: Union[Message, CallbackQuery], state: FSMContext):
    data = await state.get_data()

    # Форматируем дату в более читаемый вид
    date_str = data.get('date', 'не указана')
    if date_str != 'не указана':
        try:
            year, month, day = map(int, date_str.split('-'))
            date_str = f"{day} {get_month_name(month, case='genitive')} {year} г."
        except:
            pass
    message_text = (
        "Проверьте данные транзакции:\n\n"
        f"Категория: {data.get('category_name', 'не указана')}\n"
        f"Сумма: {data.get('amount', 0):.2f} ₽\n"
        f"Описание: {data.get('description', 'не указано')}\n"
        f"Дата: {data.get('date', 'не указана')}"
    )

    # Создаем клавиатуру для подтверждения/редактирования
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="addtx_confirm")
    builder.button(text="✏️ Категория", callback_data="addtx_edit_category")
    builder.button(text="✏️ Сумма", callback_data="addtx_edit_amount")
    builder.button(text="✏️ Описание", callback_data="addtx_edit_description")
    builder.button(text="✏️ Дата", callback_data="addtx_edit_date")
    builder.button(text="❌ Отмена", callback_data="addtx_cancel")
    builder.adjust(2, 2, 2)

    if isinstance(update, Message):
        await update.answer(message_text, reply_markup=builder.as_markup())
    else:
        await update.message.edit_text(message_text, reply_markup=builder.as_markup())

    await state.set_state(AddTransaction.waiting_for_confirmation)

@router.callback_query(F.data.startswith("addtx_edit_"))
async def edit_transaction_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split('_')[2]

    if field == "category":
        categories = await get_categories(callback.from_user.id)
        builder = InlineKeyboardBuilder()
        for category in categories:
            builder.button(
                text=category['name_category'],
                callback_data=f"addtx_category_{category['id']}"
            )
        builder.button(text="◀ Назад", callback_data="addtx_back_to_confirm")
        builder.adjust(2)

        await callback.message.edit_text(
            "Выберите новую категорию:",
            reply_markup=builder.as_markup()
        )
        await state.set_state(AddTransaction.waiting_for_category)

    elif field == "amount":
        await callback.message.edit_text(
            "Введите новую сумму транзакции (например: 1000 или 150.50):",
            reply_markup=None
        )
        await state.set_state(AddTransaction.waiting_for_amount)

    elif field == "description":
        builder = InlineKeyboardBuilder()
        builder.button(text="Пропустить", callback_data="addtx_skip_description")
        builder.button(text="◀ Назад", callback_data="addtx_back_to_confirm")
        builder.adjust(2)

        await callback.message.edit_text(
            "Введите новое описание транзакции (или нажмите 'Пропустить'):",
            reply_markup=builder.as_markup()
        )
        await state.set_state(AddTransaction.waiting_for_description)

    elif field == "date":
        builder = InlineKeyboardBuilder()
        builder.button(text="Сегодня", callback_data="addtx_date_today")
        builder.button(text="Ввести дату", callback_data="addtx_date_custom")
        builder.button(text="◀ Назад", callback_data="addtx_back_to_confirm")
        builder.adjust(2)

        await callback.message.edit_text(
            "Выберите новую дату транзакции:",
            reply_markup=builder.as_markup()
        )
        await state.set_state(AddTransaction.waiting_for_date)

    await callback.answer()

@router.callback_query(F.data == "addtx_back_to_confirm")
async def back_to_confirmation(callback: CallbackQuery, state: FSMContext):
    await show_confirmation(callback, state)
    await callback.answer()

@router.callback_query(F.data == "addtx_confirm")
async def confirm_transaction(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        # Создаем транзакцию в базе данных
        transaction_data = {
            "description": data.get('description'),
            "full_sum": data['amount'],
            "date": data.get('date', datetime.now().strftime("%Y-%m-%d")),
            "category_id": data['category_id'],
            'user_id': callback.from_user.id
        }

        # Здесь вызываем метод для создания транзакции в БД
        await create_transaction(params={'user_id': callback.from_user.id}, data=transaction_data)

        await callback.message.edit_text(
            "✅ Транзакция успешно добавлена!",
            reply_markup=None
        )
    except Exception as e:
        await callback.message.edit_text(
            f"⚠️ Ошибка при добавлении транзакции: {e}",
            reply_markup=None
        )
    finally:
        await state.clear()
    await callback.answer()

@router.callback_query(F.data == "addtx_cancel")
async def cancel_transaction(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Добавление транзакции отменено",
        reply_markup=None
    )
    await callback.answer()

@router.message(F.text == 'Изменить запись')
async def update_transaction_start(message: Message, state: FSMContext):
    """Шаг 1: Показ списка транзакций для выбора."""
    user_id = message.from_user.id
    user_pages[user_id] = 0

    try:
        message_text, total_pages = await get_paginated_transactions(user_id, 0)
        if total_pages == 0:
            await message.answer("У вас пока нет записей для изменения.")
            return

        keyboard = await build_pagination_keyboard_for_update(0, total_pages, user_id)
        await message.answer(
            "Какую запись вы хотите изменить?\n\n" + message_text,
            reply_markup=keyboard
        )
        await state.set_state(TransactionStates.waiting_for_selection)

    except Exception as e:
        print(f"Ошибка в update_transaction_start: {e}")
        await message.answer("Произошла ошибка при загрузке ваших записей. Попробуйте позже.")

@router.callback_query(F.data.startswith("transactionU_"), StateFilter(TransactionStates.waiting_for_selection))
async def handle_pagination_for_update(callback: CallbackQuery, state: FSMContext):
    """Шаг 1.1: Обработка пагинации списка транзакций."""
    data_parts = callback.data.split('_')
    action = data_parts[1]
    user_id = int(data_parts[2])
    current_page = user_pages.get(user_id, 0)

    all_transactions = await get_transactions(user_id) # Получаем ВСЕ транзакции для расчета страниц
    total_pages = math.ceil(len(all_transactions) / PAGE_SIZE) if all_transactions else 1

    new_page = current_page

    if action == "prev":
            new_page = max(0, current_page - 1)
    elif action == "next":
            new_page = min(total_pages - 1, current_page + 1)
    elif action == "back5":
            new_page = max(0, current_page - 5)
    elif action == "forward5":
            new_page = min(total_pages - 1, current_page + 5)
    elif action == "first":
            new_page = 0
    elif action == "last":
            new_page = total_pages - 1
    elif action == "choose":
             # Показываем кнопки с транзакциями текущей страницы
            start_idx = current_page * PAGE_SIZE
            page_transactions = all_transactions[start_idx : start_idx + PAGE_SIZE]
            if not page_transactions:
                 await callback.answer("На этой странице нет записей.", show_alert=True)
                 return

            choose_keyboard = await choose_buttons_update(user_id, page_transactions)
            await callback.message.edit_reply_markup(reply_markup=choose_keyboard.as_markup())
            await callback.answer("Выберите запись для редактирования")
            return # Останавливаем обработку

    elif action == "back": # Обработка кнопки "Назад" из режима выбора
             message_text, _ = await get_paginated_transactions(user_id, current_page, include_ids=False)
             keyboard = await build_pagination_keyboard_for_update(current_page, total_pages, user_id)
             await callback.message.edit_text(
                "Какую запись вы хотите изменить?\n\n" + message_text,
                reply_markup=keyboard
            )
             await callback.answer()
             return # Останавливаем обработку

        # Если страница изменилась, обновляем сообщение
    if new_page != current_page:
            user_pages[user_id] = new_page
            message_text, _ = await get_paginated_transactions(user_id, new_page, include_ids=False)
            keyboard = await build_pagination_keyboard_for_update(new_page, total_pages, user_id)
            await callback.message.edit_text(
                "Какую запись вы хотите изменить?\n\n" + message_text,
                reply_markup=keyboard
            )

    await callback.answer()



@router.callback_query(F.data.startswith("select_transactionU_"), StateFilter(TransactionStates.waiting_for_selection))
async def handle_transaction_selection_for_update(callback: CallbackQuery, state: FSMContext):
    """Шаг 2: Выбор конкретной транзакции."""
    try:
        parts = callback.data.split('_')
        if len(parts) < 3 or parts[0] != 'select' or parts[1] != 'transactionU':
            await callback.answer("Ошибка в формате данных кнопки. Попробуйте снова.", show_alert=True)
            await update_transaction_start(callback.message, state)
            return
        transaction_id = int(parts[2])
        original_data = await get_transaction(transaction_id)

        if not original_data:
            await callback.answer("Не удалось найти данные этой транзакции.", show_alert=True)
            # Можно вернуть пользователя к списку
            await update_transaction_start(callback.message, state) # Показываем список заново
            return

        # Сохраняем ID, оригинальные данные и инициализируем словарь для изменений
        await state.update_data(
            transaction_id_to_update=transaction_id,
            original_data=original_data, # Сохраняем текущие значения
            updated_data={}              # Здесь будем копить изменения
        )
        await state.set_state(TransactionStates.waiting_for_confirmation)

        # Показываем меню редактирования
        await show_update_confirmation_menu(callback.message, state)
        await callback.answer()

    except Exception as e:
        print(f"Ошибка выбора транзакции для обновления: {e}")
        await callback.answer("Не удалось выбрать запись. Попробуйте снова.", show_alert=True)

async def show_update_confirmation_menu(message_or_callback: Union[Message, CallbackQuery], state: FSMContext):
    """Шаг 3: Показ меню редактирования с текущими/измененными данными."""
    data = await state.get_data()
    transaction_id = data.get('transaction_id_to_update')
    original = data.get('original_data', {})
    changes = data.get('updated_data', {})

    if not transaction_id or not original:
         # Если что-то пошло не так, лучше отменить
         print("Ошибка: Отсутствуют ID или оригинальные данные в состоянии для show_update_confirmation_menu")
         await state.clear()
         target_message = message_or_callback if isinstance(message_or_callback, Message) else message_or_callback.message
         await target_message.edit_text("Произошла ошибка. Попробуйте начать сначала.", reply_markup=None)
         return

    category_id_to_show = changes.get('category_id', original.get('category_id'))
    # Теперь category_name_to_show не сохраняется в updated_data, поэтому он будет None, если категория не менялась
    category_name_to_show = None

    # Если имя категории не установлено (т.е. оно не было в changes, что теперь всегда так),
    # пытаемся получить его из original_data или запросить по ID
    if not category_name_to_show:
        # Сначала пробуем взять имя из original_data, если оно там есть
        category_name_from_original = original.get('category_name')
        if category_name_from_original:
             category_name_to_show = category_name_from_original
        # Если имени все еще нет и у нас есть category_id, пробуем запросить по ID
        elif category_id_to_show is not None:
             user_id_for_categories = original.get('user_id') # Убедитесь, что user_id есть в original_data
             if user_id_for_categories:
                 try:
                     categories = await get_categories(user_id_for_categories)
                     cat = next((c for c in categories if c.get('id') == category_id_to_show), None)
                     if cat:
                         category_name_to_show = cat.get('name_category', f"Категория ID: {category_id_to_show}") # Берем имя или указываем ID
                     else:
                         category_name_to_show = f"Категория ID: {category_id_to_show} (не найдена)" # Категория по ID не найдена
                 except Exception as e:
                      print(f"Ошибка при получении имени категории по ID {category_id_to_show}: {e}")
                      category_name_to_show = f"Ошибка получения имени (ID: {category_id_to_show})"
             else:
                 category_name_to_show = "Не удалось получить имя категории (нет user_id)" # Нет user_id в original_data

    # Если после всех попыток имя не получено, используем дефолтное значение
    if not category_name_to_show:
         category_name_to_show = 'Неизвестно'



    amount_to_show = changes.get('full_sum', original.get('full_sum', 0))
    description_to_show = changes.get('description', original.get('description', ''))
    date_to_show_str = changes.get('date', original.get('date', ''))

    # Форматируем дату для красивого отображения
    display_date = date_to_show_str
    if date_to_show_str and isinstance(date_to_show_str, str) and '-' in date_to_show_str:
        try:
            dt_obj = datetime.strptime(date_to_show_str.split('T')[0], '%Y-%m-%d') # Убираем время, если есть
            display_date = f"{dt_obj.day} {get_month_name(dt_obj.month, case='genitive')} {dt_obj.year} г."
        except ValueError:
            display_date = date_to_show_str # Оставляем как есть, если формат неверный


    confirmation_text = (
        f"📝 Редактирование записи (ID: {transaction_id})\n\n"
        f"Текущие данные {'(с изменениями)' if changes else ''}:\n"
        f"--------------------\n"
        f"Категория: {category_name_to_show}\n"
        f"Сумма: {amount_to_show:.2f} ₽\n"
        f"Описание: {description_to_show if description_to_show else '-'}\n"
        f"Дата: {display_date}\n"
        f"--------------------\n\n"
        "Что вы хотите изменить?"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Категорию", callback_data="update_edit_category")
    builder.button(text="✏️ Сумму", callback_data="update_edit_amount")
    builder.button(text="✏️ Описание", callback_data="update_edit_description")
    builder.button(text="✏️ Дату", callback_data="update_edit_date")
    # Кнопка сохранения активна, только если есть изменения
    if changes:
        builder.button(text="✅ Сохранить изменения", callback_data="update_confirm_changes")
    else:
        builder.button(text="Изменений нет", callback_data="no_changes") # Просто кнопка-индикатор

    builder.button(text="❌ Отмена", callback_data="update_cancel")
    builder.adjust(2, 2, 1, 1) # Примерная настройка рядов


    target_message = message_or_callback if isinstance(message_or_callback, Message) else message_or_callback.message
    try:
        await target_message.edit_text(confirmation_text, reply_markup=builder.as_markup())
    except Exception as e:
        print(f"Не удалось отредактировать сообщение в show_update_confirmation_menu: {e}")
        # Можно попробовать отправить новое, если редактирование не удалось
        # await target_message.answer(confirmation_text, reply_markup=builder.as_markup())


    await state.set_state(TransactionStates.waiting_for_confirmation)


@router.callback_query(F.data == "no_changes", StateFilter(TransactionStates.waiting_for_confirmation))
async def handle_no_changes(callback: CallbackQuery):
    """Обработка нажатия кнопки 'Изменений нет'."""
    await callback.answer("Вы еще не внесли никаких изменений.", show_alert=False)


# --- Шаг 4: Обработчики редактирования полей ---

# --- 4.1 Категория ---
@router.callback_query(F.data == "update_edit_category", StateFilter(TransactionStates.waiting_for_confirmation))
async def edit_category_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    categories = await get_categories(user_id)
    if not categories:
        await callback.answer("У вас нет категорий для выбора.", show_alert=True)
        return

    await state.update_data(all_categories=categories)
    # Используем уникальный ключ пагинации для категорий при обновлении
    user_pages[f"{user_id}_update_cat"] = 0

    message_text, total_pages = await format_categories_page_update(categories, 0) # Используем свою функцию форматирования
    # Используем префикс 'update_cat_' для колбэков пагинации категорий
    keyboard = await build_pagination_keyboard_for_categories(0, total_pages, user_id, prefix="update_cat_")

    await callback.message.edit_text(
        "Выберите новую категорию:\n\n" + message_text,
        reply_markup=keyboard
    )
    await state.set_state(TransactionStates.waiting_for_new_category)
    await callback.answer()

# Вспомогательная функция форматирования для категорий (можно объединить с той, что в Add)
async def format_categories_page_update(categories: list, page: int) -> tuple[str, int]:
    total_pages = math.ceil(len(categories) / PAGE_SIZE) if categories else 1
    start_idx = page * PAGE_SIZE
    page_categories = categories[start_idx : start_idx + PAGE_SIZE]

    formatted = [f"🔖 {cat.get('name_category', 'Без имени')}" for cat in page_categories]

    if not formatted:
        return "Нет категорий на этой странице.", total_pages

    message = "Список категорий:\n\n" + "\n".join(formatted)
    message += f"\n\nСтраница {page + 1}/{total_pages}"
    return message, total_pages

# Обработчик пагинации категорий при обновлении
@router.callback_query(F.data.startswith("update_cat_"), StateFilter(TransactionStates.waiting_for_new_category)) # Фильтр должен быть update_cat_
async def handle_pagination_update_categories(callback: CallbackQuery, state: FSMContext):
    try:
        data_parts = callback.data.split('_')
        # Ожидаем формат: update_cat_ACTION_USERID
        if len(data_parts) < 4:
             print(f"Некорректный формат callback_data в handle_pagination_update_categories: {callback.data}")
             await callback.answer("Ошибка данных навигации.")
             return

        action = data_parts[2] # ACTION на 3-й позиции
        user_id = int(data_parts[3]) # USERID на 4-й позиции

        pagination_key = f"{user_id}_update_cat"
        current_page = user_pages.get(pagination_key, 0)

        state_data = await state.get_data()
        categories = state_data.get('all_categories', [])
        total_pages = math.ceil(len(categories) / PAGE_SIZE) if categories else 1

        new_page = current_page

        if action == "prev": new_page = max(0, current_page - 1)
        elif action == "next": new_page = min(total_pages - 1, current_page + 1)
        elif action == "back5": new_page = max(0, current_page - 5)
        elif action == "forward5": new_page = min(total_pages - 1, current_page + 5)
        elif action == "first": new_page = 0
        elif action == "last": new_page = total_pages - 1
        elif action == "choose":
            # Показать кнопки для выбора категорий на текущей странице
            start_idx = current_page * PAGE_SIZE
            page_categories = categories[start_idx : start_idx + PAGE_SIZE]
            if not page_categories:
                await callback.answer("Нет категорий на этой странице.", show_alert=True)
                return
            # Используем префикс 'update_cat_select_' для кнопок выбора
            keyboard = await build_category_choice_keyboard_update(page_categories, user_id) # Убедитесь, что build_category_choice_keyboard_update существует и возвращает builder.as_markup()
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await callback.answer("Выберите категорию")
            return
        # Обработчик действия "back" из пагинации (не из выбора категории!)
        elif action == "back": # Это обработчик кнопки "<" или "<<", не "Назад" из списка выбора
             pass


        if new_page != current_page:
            user_pages[pagination_key] = new_page
            message_text, _ = await format_categories_page_update(categories, new_page)
            keyboard = await build_pagination_keyboard_for_categories(new_page, total_pages, user_id, prefix="update_cat_")
            await callback.message.edit_text(
                "Выберите новую категорию:\n\n" + message_text,
                reply_markup=keyboard
            )

        await callback.answer()
    except Exception as e:
        print(f"Ошибка пагинации категорий при обновлении: {e}")
        await callback.answer("Ошибка навигации.")

# Клавиатура выбора категории (адаптированная)
async def build_category_choice_keyboard_update(categories: list, user_id: int):
    builder = InlineKeyboardBuilder()
    for category in categories:
        # Используем префикс 'update_cat_select_' для колбэка выбора
        builder.button(
            text=category['name_category'],
            callback_data=f"update_cat_select_{category['id']}"
        )
    # Кнопка Назад возвращает к пагинации категорий
    builder.button(text="◀ Назад", callback_data=f"update_cat_categories_back_{user_id}")
    builder.adjust(2)
    return builder.as_markup()

# Обработчик выбора конкретной категории
@router.callback_query(F.data.startswith("update_cat_select_"), StateFilter(TransactionStates.waiting_for_new_category))
async def update_category_selected(callback: CallbackQuery, state: FSMContext):
     category_id = int(callback.data.split('_')[3]) # update_cat_select_ID
     state_data = await state.get_data()
     categories = state_data.get('all_categories', []) # Возможно, здесь снова запрашивать не нужно
     category = next((c for c in categories if c['id'] == category_id), None)
     category_name = category['name_category'] if category else f"ID {category_id}"

     updated_data = state_data.get('updated_data', {})
     updated_data['category_id'] = category_id
     await state.update_data(updated_data=updated_data)

     await show_update_confirmation_menu(callback.message, state)
     await callback.answer(f"Категория изменена на: {category_name}")

@router.callback_query(F.data.startswith("update_cat_categories_back_"), StateFilter(TransactionStates.waiting_for_new_category))
async def back_from_category_choice_to_pagination(callback: CallbackQuery, state: FSMContext):
        print(f"DEBUG: back_from_category_choice_to_pagination called with callback.data = {callback.data}") # Отладочный принт
        data_parts = callback.data.split('_')
        # Ожидаем формат: update_cat_categories_back_USERID
        if len(data_parts) < 5 or data_parts[0] != 'update' or data_parts[1] != 'cat' or data_parts[2] != 'categories' or data_parts[3] != 'back':
             print(f"DEBUG: Некорректный формат callback_data для возврата к пагинации категорий: {callback.data}") # Отладочный принт
             await callback.answer("Ошибка данных навигации назад.")
             return

        user_id = int(data_parts[4])
        print(f"DEBUG: Parsed user_id: {user_id}") # Отладочный принт
        pagination_key = f"{user_id}_update_cat"
        current_page = user_pages.get(pagination_key, 0)
        print(f"DEBUG: Got current_page: {current_page} for key {pagination_key}") # Отладочный принт

        state_data = await state.get_data()
        categories = state_data.get('all_categories', [])
        print(f"DEBUG: Got {len(categories)} categories from state.") # Отладочный принт
        total_pages = math.ceil(len(categories) / PAGE_SIZE) if categories else 1
        print(f"DEBUG: Calculated total_pages: {total_pages}") # Отладочный принт

        message_text, _ = await format_categories_page_update(categories, current_page)
        print("DEBUG: Formatted categories page.") # Отладочный принт

        # build_pagination_keyboard_for_categories теперь принимает prefix и возвращает as_markup()
        keyboard = await build_pagination_keyboard_for_categories(current_page, total_pages, user_id, prefix="update_cat_")
        print("DEBUG: Built pagination keyboard.") # Отладочный принт

        await callback.message.edit_text(
            "Выберите новую категорию:\n\n" + message_text,
            reply_markup=keyboard
        )
        print("DEBUG: Edited message with pagination.") # Отладочный принт
        await callback.answer("Возврат к списку категорий.")
        print("DEBUG: Answered callback.") # Отладочный принт

# --- 4.2 Сумма ---
@router.callback_query(F.data == "update_edit_amount", StateFilter(TransactionStates.waiting_for_confirmation))
async def edit_amount_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TransactionStates.waiting_for_new_amount)
    # Удаляем предыдущее сообщение с меню, чтобы избежать путаницы
    try: await callback.message.delete()
    except Exception: pass
    # Отправляем новое сообщение с запросом
    await callback.message.answer(
        "Введите новую сумму транзакции (число, например: 1000 или 150.50).\n"
        "Для отмены отправьте /cancel.",
        reply_markup=None
    )
    await callback.answer()

@router.message(StateFilter(TransactionStates.waiting_for_new_amount))
async def process_new_amount(message: Message, state: FSMContext):
    if message.text.lower() == '/cancel':
         await message.answer("Изменение суммы отменено.")
         # Нужно снова показать меню, отправляем новым сообщением
         await show_update_confirmation_menu(await message.answer("Возврат в меню..."), state)
         return

    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")

        state_data = await state.get_data()
        updated_data = state_data.get('updated_data', {})
        updated_data['full_sum'] = amount
        await state.update_data(updated_data=updated_data)

        await message.answer(f"Сумма изменена на: {amount:.2f} ₽.")
        await show_update_confirmation_menu(await message.answer("Возврат в меню..."), state)

    except ValueError:
        await message.answer(
            "❌ Неверный формат суммы. Введите положительное число (например: 1000 или 150.50) или /cancel"
        )


# --- 4.3 Описание ---
@router.callback_query(F.data == "update_edit_description", StateFilter(TransactionStates.waiting_for_confirmation))
async def edit_description_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TransactionStates.waiting_for_new_description)
    try: await callback.message.delete()
    except Exception: pass
    await callback.message.answer(
        "Введите новое описание транзакции.\n"
        "Для отмены отправьте /cancel.",
        reply_markup=None
    )
    await callback.answer()

@router.message(StateFilter(TransactionStates.waiting_for_new_description))
async def process_new_description(message: Message, state: FSMContext):
    if message.text.lower() == '/cancel':
         await message.answer("Изменение описания отменено.")
         await show_update_confirmation_menu(await message.answer("Возврат в меню..."), state)
         return

    description = message.text.strip()
    if not description:
        description = None
    state_data = await state.get_data()
    updated_data = state_data.get('updated_data', {})
    updated_data['description'] = description
    await state.update_data(updated_data=updated_data)

    await message.answer(f"Описание изменено.")
    await show_update_confirmation_menu(await message.answer("Возврат в меню..."), state)


# --- 4.4 Дата ---
@router.callback_query(F.data == "update_edit_date", StateFilter(TransactionStates.waiting_for_confirmation))
async def edit_date_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(TransactionStates.waiting_for_new_date)
    # Используем префикс 'update_date_' для колбэков календаря
    keyboard = await get_calendar_keyboard(prefix="update_date_")
    await callback.message.edit_text(
        "🗓 Выберите новую дату из календаря:",
        reply_markup=keyboard
    )
    await callback.answer()

# Обработчик выбора дня в календаре
@router.callback_query(F.data.startswith("update_date_calendar_day"), StateFilter(TransactionStates.waiting_for_new_date))
async def handle_update_calendar_day_selection(callback: types.CallbackQuery, state: FSMContext):
    try:
        parts = callback.data.split("_")
        year, month, day = map(int, parts[-3:])
        selected_date = f"{year}-{month:02d}-{day:02d}" # Формат YYYY-MM-DD

        state_data = await state.get_data()
        updated_data = state_data.get('updated_data', {})
        updated_data['date'] = selected_date
        await state.update_data(updated_data=updated_data)

        await show_update_confirmation_menu(callback.message, state)
        # Форматируем дату для ответа
        dt_obj = datetime.strptime(selected_date, '%Y-%m-%d')
        display_date = f"{dt_obj.day} {get_month_name(dt_obj.month, case='genitive')} {dt_obj.year} г."
        await callback.answer(f"Дата изменена на: {display_date}")

    except Exception as e:
        print(f"Ошибка обработки выбора даты в календаре для обновления: {e}")
        await callback.answer("Ошибка выбора даты.")

# Обработчики навигации календаря (prev/next month)
@router.callback_query(F.data.startswith("update_date_"), StateFilter(TransactionStates.waiting_for_new_date))
async def handle_update_calendar_navigation(callback: types.CallbackQuery, state: FSMContext):
    try:
        parts = callback.data.split("_")
        # Ожидаем формат: update_date_ACTION_...
        if len(parts) < 3: # Минимум 3 части: update_date_ACTION
             print(f"Недостаточно частей в callback_data для навигации календаря: {callback.data}")
             await callback.answer("Ошибка данных календаря.")
             return

        action_type = parts[2] # ACTION теперь на 3-й позиции (индекс 2)

        # Обрабатываем только prev и next здесь
        if action_type not in ["prev", "next"]:
             # Если это не prev или next, возможно, это day, confirm или cancel,
             # которые должны обрабатываться другими функциями.
             # Проигнорируем этот callback здесь или добавим логику, если нужно.
             # Так как day, confirm, cancel имеют свои обработчики, этот else не должен выполняться при корректной работе.
             print(f"DEBUG: handle_update_calendar_navigation получил не prev/next action: {callback.data}")
             await callback.answer() # Просто отвечаем, чтобы убрать часы
             return


        # Парсим год и месяц только для prev/next
        if len(parts) < 5: # update_date_ACTION_YEAR_MONTH -> минимум 5 частей
             print(f"Недостаточно частей для prev/next в handle_update_calendar_navigation: {callback.data}")
             await callback.answer("Ошибка данных календаря для навигации.")
             return

        year, month = int(parts[3]), int(parts[4]) # YEAR и MONTH на 4-й и 5-й позициях

        if action_type == "prev":
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        elif action_type == "next":
            month += 1
            if month == 13:
                month = 1
                year += 1

        # Вызываем generate_calendar с полным префиксом
        keyboard = generate_calendar(year, month, prefix="update_date_calendar_") # Используем полный префикс
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    except Exception as e:
        print(f"Ошибка навигации календаря (update): {e}")
        await callback.answer("Ошибка навигации календаря.")

@router.callback_query(F.data == "update_date_calendar_confirm", StateFilter(TransactionStates.waiting_for_new_date))
async def handle_update_calendar_confirm(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение выбора даты в календаре при обновлении."""
    # Дата уже должна быть сохранена в состоянии в handle_update_calendar_day_selection
    data = await state.get_data()
    if 'date' not in data.get('updated_data', {}):
         await callback.answer("Сначала выберите дату.", show_alert=True)
         return

    await show_update_confirmation_menu(callback.message, state) # Возвращаемся в меню подтверждения
    await callback.answer("Дата подтверждена.")

@router.callback_query(F.data == "update_cat_back_to_confirm", StateFilter(TransactionStates.waiting_for_new_category))
async def back_from_category_selection_to_confirm(callback: CallbackQuery, state: FSMContext):
    """Возврат из выбора категории в меню подтверждения обновления."""
    await show_update_confirmation_menu(callback.message, state)
    await callback.answer()
    
# Обработчик кнопки "Отмена" в календаре при редактировании даты
@router.callback_query(F.data == "update_date_calendar_cancel", StateFilter(TransactionStates.waiting_for_new_date))
async def handle_update_calendar_cancel(callback: types.CallbackQuery, state: FSMContext):
    """Отмена выбора даты в календаре при обновлении."""
    # Возвращаемся в меню подтверждения, не сохраняя изменения даты
    await show_update_confirmation_menu(callback.message, state)
    await callback.answer("Выбор даты отменен.")

# --- Шаг 5: Сохранение и Отмена ---

@router.callback_query(F.data == "update_confirm_changes", StateFilter(TransactionStates.waiting_for_confirmation))
@router.callback_query(F.data == "update_confirm_changes")
async def confirm_update_changes(callback: CallbackQuery, state: FSMContext):
    """Подтверждение обновления транзакции"""
    data = await state.get_data()
    transaction_id = data.get("transaction_id_to_update")
    original_data = data.get("original_data", {})
    updated_data = data.get("updated_data", {})
    payload_to_send = original_data.copy()
    payload_to_send.update(updated_data)
    user_id = callback.from_user.id

    try:
        result = await update_transaction(transaction_id, payload_to_send, user_id)
        await callback.message.edit_text(
            "✅ Запись успешно обновлена!",
            reply_markup=None
        )
    except Exception as e:
        # Логирование ошибки уже добавлено в update_transaction
        await callback.message.edit_text(
            f"⚠️ Ошибка при обновлении: {e}",
            reply_markup=None
        )
    finally:
        await state.clear()
    await callback.answer()


@router.callback_query(F.data == "update_cancel", StateFilter(TransactionStates))
async def cancel_update_process(callback: CallbackQuery, state: FSMContext):
    """Отмена всего процесса обновления."""
    await state.clear()
    await callback.message.edit_text("❌ Обновление записи отменено.", reply_markup=None)
    # Можно добавить кнопку возврата в меню
    # await callback.message.answer("Возврат в главное меню.", reply_markup=await start_keyboard())
    await callback.answer()





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
        await message.answer('🙂 Вот список ваших записей! Какую из них хотите удалить?\n\n'+message_text,
                           reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Ошибка при получении транзакций: {e}")

@router.callback_query(F.data.startswith("transactionD_"))
async def handle_pagination_for_delete(callback: CallbackQuery, state: FSMContext):
    try:
        data_parts = callback.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        current_page = user_pages.get(user_id, 0)
        all_transactions = await get_transactions(user_id)
        total_pages = (len(all_transactions) + PAGE_SIZE - 1) // PAGE_SIZE

        # Остальная логика пагинации...
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

        await state.update_data(original_message=message_text)
        await callback.message.edit_text(text=message_text, reply_markup=keyboard)
        await callback.answer()

    except Exception as e:
        print(f"Ошибка пагинации: {e}")
        await callback.answer("Произошла ошибка, попробуйте позже")

@router.callback_query(F.data.startswith("select_transactionD_"))
async def handle_transaction_selection_for_delete(callback: CallbackQuery, state: FSMContext):
    transaction_id = int(callback.data.split('_')[2])
    # transaction_name = str(callback.data.split('_')[3]) # Ненадежно
    # Лучше получить данные транзакции из БД по transaction_id

    # Получаем данные транзакции для отображения имени
    # Это может быть неэффективно, лучше иметь функцию get_transaction(id)
    all_user_transactions = await get_transactions(callback.from_user.id)
    selected_transaction = next((tx for tx in all_user_transactions if tx['id'] == transaction_id), None)

    if not selected_transaction:
         await callback.answer("Не удалось найти данные этой транзакции для удаления.", show_alert=True)
         # Вернуть пользователя к списку
         await handle_delete_flow(callback.from_user.id, callback.message, state)
         return

    transaction_name_for_message = selected_transaction.get('description', f"Транзакция {transaction_id}")


    await state.update_data(selected_transaction_id=transaction_id)
    # await state.update_data(selected_transaction_name=transaction_name) # Эта строка больше не нужна, имя получаем по ID

    # Получаем оригинальное сообщение со списком записей
    # Этот подход может быть ненадежным, если сообщение изменилось
    # Лучше перегенерировать список или просто показать сообщение о подтверждении
    # data = await state.get_data()
    # original_message = data.get('original_message', "Список транзакций")
    original_message = "Список ваших записей" # Более безопасный вариант

    # Создание клавиатуры через билдер
    builder = await confirm_or_cancel_buttons()

    await callback.message.edit_text(
        text=f"{original_message}\n\n"
             f"Выбрана запись: '{transaction_name_for_message}'\n"
             "❗️Вы уверены, что хотите удалить эту запись?",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_delete")
async def confirm_delete_transaction(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    transaction_id = data.get("selected_transaction_id")
    # transaction_name = data.get("selected_transaction_name") # Больше не нужно

    if transaction_id is not None:
        try:
            res = await delete_transaction(transaction_id)
             # Проверить ответ сервера res, чтобы убедиться, что удаление прошло успешно
            if res: # Проверьте, что res != None и/или содержит подтверждение успеха
                await callback.message.answer(
                    text=f"🗑 Готово! Ваша запись успешно удалена 😊",
                    reply_markup=None # Убираем клавиатуру
                )
                # Можно добавить клавиатуру для возврата в меню или к списку
                await callback.message.answer("Выберите действие:", reply_markup=await back_menu_or_list_transactions())
            else:
                 # Если res пустой или не указывает на успех
                 await callback.message.edit_text("⚠️ Не удалось подтвердить удаление записи.")

        except Exception as e: # Перехватываем ошибки удаления (например, HTTPStatusError)
             print(f"Ошибка при удалении транзакции ID {transaction_id}: {e}")
             await callback.message.edit_text(f"⚠️ Произошла ошибка при удалении записи: {e}")

    else:
        await callback.message.edit_text("⚠️ Ошибка: ID транзакции для удаления не найден.")

    await callback.answer()
    await state.clear() # Очищаем состояние после попытки удаления

@router.callback_query(F.data == "cancel_delete")
async def cancel_delete_transaction(callback: CallbackQuery, state: FSMContext):
    # builder = await back_menu_or_list_transactions() # Клавиатура уже создается в handle_delete_flow
    await callback.message.answer("🙂 Хотите удалить другую запись или вернуться в главное меню?",
            reply_markup=await back_menu_or_list_transactions()) # Создаем клавиатуру здесь
    await state.clear()
    await callback.answer()



@router.message(F.text == 'История моих записей')
async def show_transactions(message: Message):
    user_id = message.from_user.id
    user_pages[user_id] = 0  # Сбрасываем на первую страницу

    try:
        # Убираем include_ids=False, если get_paginated_transactions его не принимает
        message_text, total_pages = await get_paginated_transactions(user_id, 0)
        keyboard = await build_pagination_keyboard_for_show(0, total_pages, user_id)
        await message.answer('📂 Вот список всех записей😊 :\n\n'+message_text, reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Ошибка при получении транзакций: {e}")

@router.callback_query(F.data.startswith("transactions_"))
async def handle_pagination_for_show(callback: CallbackQuery):
    try:
        data_parts = callback.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        current_page = user_pages.get(user_id, 0)
        # Получаем все транзакции, чтобы рассчитать total_pages
        all_transactions = await get_transactions(user_id)
        total_pages = math.ceil(len(all_transactions) / PAGE_SIZE) if all_transactions else 1

        # Определяем новую страницу (используем логику check_action, но без его вызова, если он не нужен)
        new_page = current_page
        if action == "prev": new_page = max(0, current_page - 1)
        elif action == "next": new_page = min(total_pages - 1, current_page + 1)
        elif action == "back5": new_page = max(0, current_page - 5)
        elif action == "forward5": new_page = min(total_pages - 1, current_page + 5)
        elif action == "first": new_page = 0
        elif action == "last": new_page = total_pages - 1
        # Для истории нет действия 'choose'

        # if new_page is None: # check_action возвращает None при choose/back, здесь это не применимо
        #     return

        # Только если страница действительно изменилась, обновляем сообщение
        if new_page != current_page:
             user_pages[user_id] = new_page
             # Получаем текст для новой страницы
             # Убираем include_ids=False, если get_paginated_transactions его не принимает
             message_text, total_pages = await get_paginated_transactions(user_id, new_page)
             keyboard = await build_pagination_keyboard_for_show(new_page, total_pages, user_id)

             await callback.message.edit_text(message_text, reply_markup=keyboard)

        await callback.answer() # Отвечаем на колбэк в конце

    except Exception as e:
        print(f"Ошибка пагинации истории: {e}")
        await callback.answer(f"Произошла ошибка, попробуйте позже")