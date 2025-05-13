from aiogram import types
from typing import Any, Dict, Optional, Union
from aiogram import Router, F
import re
from aiogram.filters import or_f,StateFilter,and_f
from aiogram.types import Message, CallbackQuery,ReplyKeyboardRemove
from project.bot.conecting_methods.category import get_categories
from project.bot.conecting_methods.methods import check_action
from project.bot.handlers.statistic import get_month_name
from project.bot.keyboards.calendar_keyboard import generate_calendar, generate_edit_calendar, get_calendar_keyboard, get_edit_calendar_keyboard
from project.bot.messages.messages import *
from aiogram.fsm.context import FSMContext
from project.bot.states import *
from project.bot.keyboards.reply import *
from project.bot.Save import save
from datetime import datetime
import calendar
from project.bot.keyboards.inline_transactions import build_category_choice_keyboard, build_pagination_keyboard_for_categories
from project.bot.conecting_methods.transactions import create_transaction, delete_transaction, get_transactions,update_transaction
from project.bot.messages.mesage_transaction import PAGE_SIZE, get_paginated_transactions
from project.bot.keyboards.inline_transactions import (back_menu_or_list_transactions,
                                                       build_pagination_keyboard_for_delete, build_pagination_keyboard_for_show, confirm_or_cancel_buttons)
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

@router.message(F.text == 'Добaвить запись')
async def add_transaction_start(message: Message, state: FSMContext):
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
            "💸 Давайте создадим новую запись! Пожалуйста, выберите категорию:\n\n" + message_text,
            reply_markup=keyboard
        )
        await message.answer(
            "⬆️⬆️",
            reply_markup=ReplyKeyboardRemove()
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
                text="💸 Давайте создадим новую запись! Пожалуйста, выберите категорию:\n\n" + message_text,
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
                text="💸 Давайте создадим новую запись! Пожалуйста, выберите категорию:\n\n" + message_text,
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
            "Пожалуйста, введите сумму записи 💸\n"
            "Пример: 1000 или 150.50\n",
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
        builder.button(text="❌ Отмена", callback_data="addtx_cancel")
        builder.adjust(2)
        
        await message.answer(
            f"Сумма: {amount:.2f} ₽\n\n"
            "📝 Введите описание для вашей записи:",
            reply_markup=builder.as_markup()
        )
    except ValueError:
        await message.answer("Некорректная сумма 😔\n"
        "Пожалуйста, введите число — например: 1000 или 150.50 💰")

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
        "Выберите дату записи:",
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
        "Ура! Теперь укажи дату 📅😊",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data == "addtx_date_today")
async def set_date_today(callback: CallbackQuery, state: FSMContext):
    today = datetime.now().strftime("%Y-%m-%d")
    await state.update_data(date=today)
    await show_confirmation(callback, state)
    await callback.answer()

@router.callback_query(F.data == "addtx_date_custom")
async def ask_custom_date(callback: types.CallbackQuery, state: FSMContext):
    """Показывает календарь для выбора даты"""
    keyboard = await get_calendar_keyboard()
    await callback.message.edit_text(
        "🗓 Выберите дату из календаря:",
        reply_markup=keyboard
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
            "Выберите дату записи:",
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
        "Проверьте данные записи 📋\n\n"
        f"Категория: {data.get('category_name', 'не указана')}\n"
        f"Сумма: {data.get('amount', 0):.2f} ₽\n"
        f"Описание: {data.get('description', 'не указано')}\n"
        f"Дата: {date_str}\n\n"
        f"Всё верно? 😊\n"
        f"Если да — подтвердите.\n"
        f"Если нужно что-то изменить — выберите, что именно хотите поменять!"
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
        builder.button(text="< Назад", callback_data="addtx_back_to_confirm")
        builder.adjust(2)
        
        await callback.message.edit_text(
            "Выберите новую категорию:",
            reply_markup=builder.as_markup()
        )
        await state.set_state(AddTransaction.waiting_for_category)
    
    elif field == "amount":
        await callback.message.edit_text(
            "Введите новую сумму записи (например: 1000 или 150.50):",
            reply_markup=None
        )
        await state.set_state(AddTransaction.waiting_for_amount)
    
    elif field == "description":
        builder = InlineKeyboardBuilder()
        builder.button(text="Пропустить", callback_data="addtx_skip_description")
        builder.button(text="< Назад", callback_data="addtx_back_to_confirm")
        builder.adjust(2)
        
        await callback.message.edit_text(
            "Введите новое описание записи (или нажмите 'Пропустить'):",
            reply_markup=builder.as_markup()
        )
        await state.set_state(AddTransaction.waiting_for_description)
    
    elif field == "date":
        builder = InlineKeyboardBuilder()
        builder.button(text="Сегодня", callback_data="addtx_date_today")
        builder.button(text="Ввести дату", callback_data="addtx_date_custom")
        builder.button(text="< Назад", callback_data="addtx_back_to_confirm")
        builder.adjust(2)
        
        await callback.message.edit_text(
            "Выберите новую дату записи:",
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
        # Создаем записи в базе данных
        transaction_data = {
            "description": data.get('description'),
            "full_sum": data['amount'],
            "date": data.get('date', datetime.now().strftime("%Y-%m-%d")),
            "category_id": data['category_id'],
            'user_id': callback.from_user.id
        }
        
        # Здесь вызываем метод для создания записи в БД
        await create_transaction(params={'user_id': callback.from_user.id}, data=transaction_data)
        
        await callback.message.answer(
            "✅ Ваша запись успешно добавлена!\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        await callback.message.edit_text(
            f"⚠️ Ошибка при добавлении записи: {e}\n"+str(transaction_data),
            reply_markup=None
        )
    finally:
        await state.clear()
    await callback.answer()

@router.callback_query(F.data == "addtx_cancel")
async def cancel_transaction(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ Добавление записи отменено",
        reply_markup=await start_keyboard()
    )
    await callback.answer()










@router.message(F.text == 'Изменить запись')
async def start_update_transaction(message: Message, state: FSMContext):
    """Начало процесса обновления"""
    await state.set_state(UpdateTransactionForm.select_transaction)
    user_id = message.from_user.id
    user_pages[user_id] = 0

    try:
        transactions = await get_transactions(user_id)
        if not transactions:
            await message.answer("📭 У вас нет транзакций для редактирования")
            return

        await show_transactions_page(message, user_id, 0, transactions)
        await message.answer(
        "⬆️⬆️",
        reply_markup=ReplyKeyboardRemove()
    )
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")

async def show_edit_menu(
    source: Union[Message, CallbackQuery], 
    transaction: Dict[str, Any], 
    user_id: int
):
    """Отображение меню редактирования"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✏️ Сумму", callback_data="edit_transaction_amount")
    builder.button(text="✏️ Описание", callback_data="edit_transaction_description")
    builder.button(text="✏️ Дату", callback_data="edit_transaction_date")
    builder.button(text="✅ Подтвердить", callback_data="confirm_transaction_update")
    builder.button(text="❌ Отменить", callback_data="cancel_transaction_update")
    
    builder.adjust(3, 2)
    
    text = await format_transaction_details(transaction)
    
    if isinstance(source, Message):
        await source.answer(text, reply_markup=builder.as_markup())
    else:
        await source.message.edit_text(text, reply_markup=builder.as_markup())

async def show_transactions_page(
    source: Union[Message, CallbackQuery],
    user_id: int,
    page: int,
    transactions: list
):
    """Отображение страницы с транзакциями"""
    total_pages = max(1, (len(transactions) + PAGE_SIZE - 1) // PAGE_SIZE)
    start_idx = page * PAGE_SIZE
    page_transactions = transactions[start_idx:start_idx + PAGE_SIZE]
    
    builder = InlineKeyboardBuilder()
    
    # Кнопки транзакций
    for tx in page_transactions:
        builder.button(
            text=f"{tx.get('category_name', '?')} | {float(tx.get('full_sum', 0)):.2f} ₽",
            callback_data=f"select_tx_{tx['id']}"
        )
    
    # Кнопки пагинации
    if page > 0:
        builder.button(text="⬅️ Назад", callback_data=f"tx_prev_{user_id}")
    if page < total_pages - 1:
        builder.button(text="Вперед ➡️", callback_data=f"tx_next_{user_id}")
    
    builder.button(text="❌ Отмена", callback_data="cancel_transaction_update")
    builder.adjust(1, *[1 for _ in page_transactions], 2, 1)
    
    text = f"📝 Выберите транзакцию (стр. {page + 1}/{total_pages}):"
    
    if isinstance(source, Message):
        await source.answer(text, reply_markup=builder.as_markup())
    else:
        await source.message.edit_text(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("tx_"))
async def handle_transaction_pagination(callback: CallbackQuery, state: FSMContext):
    """Обработка пагинации транзакций"""
    try:
        action = callback.data.split('_')[1]
        user_id = int(callback.data.split('_')[2])
        current_page = user_pages.get(user_id, 0)

        transactions = await get_transactions(user_id)
        total_pages = max(1, (len(transactions) + PAGE_SIZE - 1) // PAGE_SIZE)

        new_page = current_page
        if action == "prev":
            new_page = max(0, current_page - 1)
        elif action == "next":
            new_page = min(total_pages - 1, current_page + 1)

        if new_page != current_page:
            user_pages[user_id] = new_page
            await show_transactions_page(callback, user_id, new_page, transactions)

        await callback.answer()
    except Exception as e:
        print(f"Transaction pagination error: {e}")
        await callback.answer("⚠️ Ошибка пагинации")

@router.callback_query(F.data.startswith("select_tx_"))
async def select_transaction_handler(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора транзакции"""
    try:
        tx_id = int(callback.data.split('_')[2])
        user_id = callback.from_user.id

        transactions = await get_transactions(user_id)
        selected = next((tx for tx in transactions if tx['id'] == tx_id), None)

        if not selected:
            await callback.answer("⚠️ Транзакция не найдена")
            return

        await state.update_data(
            transaction_id=tx_id,
            current_transaction=selected
        )

        await show_edit_menu(callback, selected, user_id)
        await callback.answer()
    except Exception as e:
        print(f"Select transaction error: {e}")
        await callback.answer("⚠️ Ошибка выбора")

@router.callback_query(F.data == "edit_transaction_category")
async def start_category_selection(callback: CallbackQuery, state: FSMContext):
    """Начало выбора категории"""
    await state.set_state(UpdateTransactionForm.select_category)
    user_id = callback.from_user.id

    categories = await get_categories(user_id)
    user_categories = [c for c in categories if c.get('user_id')]

    if not user_categories:
        await callback.answer("❌ Нет доступных категорий")
        return

    await state.update_data(all_categories=user_categories)
    user_pages[user_id] = 0

    await show_categories_page(callback, user_id, 0, user_categories)
    await callback.answer()

async def show_categories_page(
    callback: CallbackQuery,
    user_id: int,
    page: int,
    categories: list
):
    """Отображение страницы категорий"""
    total_pages = max(1, (len(categories) + PAGE_SIZE - 1) // PAGE_SIZE)
    start_idx = page * PAGE_SIZE
    page_categories = categories[start_idx:start_idx + PAGE_SIZE]
    
    builder = InlineKeyboardBuilder()
    
    # Кнопки категорий
    for cat in page_categories:
        builder.button(
            text=f"{cat['name_category']} ({'💰' if cat['type'] == 1 else '💸'})",
            callback_data=f"select_cat_{cat['id']}"
        )
    
    # Кнопки пагинации
    if page > 0:
        builder.button(text="⬅️ Назад", callback_data=f"cat_prev_{user_id}")
    if page < total_pages - 1:
        builder.button(text="Вперед ➡️", callback_data=f"cat_next_{user_id}")
    
    builder.button(text="◀ Назад", callback_data="back_to_edit_menu")
    builder.button(text="❌ Отмена", callback_data="cancel_transaction_update")
    
    builder.adjust(1, *[1 for _ in page_categories], 2, 2)
    
    text = (
        f"📋 Выберите категорию (стр. {page + 1}/{total_pages}):\n\n"
        f"💰 - Доход\n💸 - Расход"
    )
    
    await safe_edit_message(callback, text, builder)

@router.callback_query(
    F.data.startswith("cat_"),
    UpdateTransactionForm.select_category
)
async def handle_category_pagination(callback: CallbackQuery, state: FSMContext):
    """Пагинация категорий"""
    try:
        action = callback.data.split('_')[1]
        user_id = int(callback.data.split('_')[2])
        current_page = user_pages.get(user_id, 0)

        data = await state.get_data()
        categories = data.get('all_categories', [])
        total_pages = max(1, (len(categories) + PAGE_SIZE - 1) // PAGE_SIZE)

        new_page = current_page
        if action == "prev":
            new_page = max(0, current_page - 1)
        elif action == "next":
            new_page = min(total_pages - 1, current_page + 1)

        if new_page != current_page:
            user_pages[user_id] = new_page
            await show_categories_page(callback, user_id, new_page, categories)

        await callback.answer()
    except Exception as e:
        print(f"Category pagination error: {e}")
        await callback.answer("⚠️ Ошибка пагинации")

@router.callback_query(
    F.data.startswith("select_cat_"),
    UpdateTransactionForm.select_category
)
async def select_category_handler(callback: CallbackQuery, state: FSMContext):
    """Выбор категории"""
    try:
        cat_id = int(callback.data.split('_')[2])
        data = await state.get_data()
        categories = data.get('all_categories', [])

        selected = next((c for c in categories if c['id'] == cat_id), None)
        if not selected:
            await callback.answer("⚠️ Категория не найдена")
            return

        # Обновляем транзакцию
        transaction = data['current_transaction'].copy()
        transaction.update({
            'category_id': selected['id'],
            'category_name': selected['name_category']
        })

        await state.update_data(current_transaction=transaction)
        await state.set_state(UpdateTransactionForm.confirmation)
        await show_edit_menu(callback, transaction, callback.from_user.id)
        await callback.answer(f"✅ Выбрано: {selected['name_category']}")
    except Exception as e:
        print(f"Select category error: {e}")
        await callback.answer("⚠️ Ошибка выбора")

@router.callback_query(F.data == "back_to_edit_menu")
async def back_to_edit_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в меню редактирования"""
    data = await state.get_data()
    await state.set_state(UpdateTransactionForm.confirmation)
    await show_edit_menu(callback, data['current_transaction'], callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "confirm_transaction_update")
async def confirm_update_handler(callback: CallbackQuery, state: FSMContext):
    """Подтверждение обновления"""
    try:
        data = await state.get_data()
        tx_data = data['current_transaction']
        user_id = callback.from_user.id

        # --- Начало ИСПРАВЛЕННОГО блока преобразования даты ---
        date_str = tx_data['date']
        # Теперь мы знаем, что date_str может быть в двух форматах.
        # Попробуем разобрать в каждом из них.
        date_obj = None # Инициализируем как None

        try:
            # Попытка 1: Разобрать формат с сервера (YYYY-MM-DDTHH:MM:SS)
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            # Если успешно, можно отформатировать в YYYY-MM-DD сразу
            db_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            try:
                # Попытка 2: Разобрать формат после редактирования (ДД.ММ.ГГГГ)
                date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                # Если успешно, отформатировать в YYYY-MM-DD
                db_date = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                 # Если ни один формат не подошел, это ошибка
                await callback.message.edit_text(
                    "⚠️ Ошибка: Не удалось распознать формат даты. Обратитесь к администратору бота.",
                    reply_markup=None
                )
                await state.clear()
                await callback.answer()
                return # Прерываем выполнение

        # В этом месте db_date будет содержать дату в формате YYYY-MM-DD,
        # если парсинг прошел успешно

        # --- Конец ИСПРАВЛЕННОГО блока преобразования даты ---

        update_data = {
            "description": tx_data.get('description'),
            "full_sum": float(tx_data['full_sum']),
            "date": db_date, # Используем правильно отформатированную дату для БД
            "category_id": tx_data['category_id'],
        }
        # print(f"Отправляем на сервер для обновления: {update_data}") # Отладочный вывод

        # !!! Важно: Убедитесь, что здесь вызывается update_transaction и НЕТ аргумента user_id !!!
        await update_transaction(
            transaction_id=data['transaction_id'],
            update_data=update_data,
            user_id=user_id
        )

        # Форматируем дату для отображения пользователю (используем date_obj из успешного парсинга)
        display_date = date_obj.strftime("%d.%m.%Y") # Формат для отображения

            # Получаем описание с безопасным доступом
        description_text = tx_data.get('description', 'Нет описания')
        # Получаем название категории с безопасным доступом
        category_name_text = tx_data.get('category_name', 'Без категории')


        await callback.message.answer(
            "✅ Транзакция успешно обновлена!\n\n"
            f"📁 Категория: {category_name_text}\n"
            f"💰 Сумма: {float(tx_data['full_sum']):.2f} ₽\n"
            f"📝 Описание: {description_text}\n"
            f"📅 Дата: {display_date}", reply_markup= await start_keyboard()
        )
        await state.clear()

    except Exception as e:
        await callback.message.edit_text(f"❌ Произошла ошибка при обновлении записи: {str(e)}")
    finally:
        await callback.answer()

@router.callback_query(F.data == "cancel_transaction_update")
async def cancel_update_handler(callback: CallbackQuery, state: FSMContext):
    """Отмена обновления"""
    await state.clear()
    await callback.message.answer("❌ Редактирование отменено",
                                  reply_markup=await start_keyboard())

# Обработчики редактирования других полей (аналогично категории)
@router.callback_query(F.data == "edit_transaction_amount")
async def edit_amount_handler(callback: CallbackQuery, state: FSMContext):
    """Редактирование суммы"""
    await state.set_state(UpdateTransactionForm.new_value)
    await state.update_data(edit_field="amount")

    builder = InlineKeyboardBuilder()
    builder.button(text="◀ Назад", callback_data="back_to_edit_menu")
    builder.button(text="❌ Отмена", callback_data="cancel_transaction_update")
    builder.adjust(2)

    await callback.message.edit_text(
        "💰 Введите новую сумму (например: 1500.50):",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "edit_transaction_description")
async def edit_description_handler(callback: CallbackQuery, state: FSMContext):
    """Редактирование описания"""
    await state.set_state(UpdateTransactionForm.new_value)
    await state.update_data(edit_field="description")

    builder = InlineKeyboardBuilder()
    builder.button(text="◀ Назад", callback_data="back_to_edit_menu")
    builder.button(text="❌ Отмена", callback_data="cancel_transaction_update")
    builder.adjust(2)

    await callback.message.edit_text(
        "📝 Введите новое описание:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "edit_transaction_date")
async def edit_date_handler(callback: CallbackQuery, state: FSMContext):
    """Редактирование даты через календарь"""
    await state.set_state(UpdateTransactionForm.new_value)
    await state.update_data(edit_field="date")

    keyboard = await get_edit_calendar_keyboard()
    await callback.message.edit_text(
        "📅 Выберите новую дату из календаря:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_calendar_"))
async def handle_edit_calendar_actions(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[2]
    
    if action == "day":
        # Обработка выбора дня
        _, _, _, year, month, day = callback.data.split("_")
        selected_date = f"{day}.{month}.{year}"  # Формат для отображения
        
        await process_field_update(callback, selected_date, state)
        
    elif action == "prev":
        # Переход к предыдущему месяцу
        _, _, _, year, month = callback.data.split("_")
        year, month = int(year), int(month)
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        keyboard = generate_edit_calendar(year, month)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        
    elif action == "next":
        # Переход к следующему месяцу
        _, _, _, year, month = callback.data.split("_")
        year, month = int(year), int(month)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        keyboard = generate_edit_calendar(year, month)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    await callback.answer()

@router.callback_query(F.data == "use_today_date")
async def use_today_date_handler(callback: CallbackQuery, state: FSMContext):
    """Использование текущей даты"""
    today = datetime.now().strftime("%d.%m.%Y")
    await process_field_update(callback, today, state)
    await callback.answer()

@router.message(UpdateTransactionForm.new_value)
async def process_new_value(message: Message, state: FSMContext):
    """Обработка нового значения"""
    await process_field_update(message, message.text, state)

async def process_field_update(
    source: Union[Message, CallbackQuery],
    value: str,
    state: FSMContext
):
    """Общая обработка обновления поля"""
    data = await state.get_data()
    field = data['edit_field']
    transaction = data['current_transaction'].copy()

    try:
        if field == "amount":
            new_value = float(value.replace(',', '.'))
            if new_value <= 0:
                raise ValueError("Сумма должна быть положительной")
            transaction['full_sum'] = new_value
        elif field == "date":
            datetime.strptime(value, "%d.%m.%Y")  # Валидация формата ДД.ММ.ГГГГ
            transaction['date'] = value
        else:
            transaction[field] = value

        await state.update_data(current_transaction=transaction)
        await state.set_state(UpdateTransactionForm.confirmation)
        # Определяем user_id в зависимости от типа источника (Message или CallbackQuery)
        user_id = source.from_user.id if isinstance(source, Message) else source.from_user.id
        await show_edit_menu(source, transaction, user_id)

    except ValueError as e:
        error_msg = {
            "amount": "⚠️ Введите корректную сумму (например: 1500.50)",
            "date": "⚠️ Введите дату в формате ДД.ММ.ГГГГ"
        }.get(field, "⚠️ Некорректное значение")

        if isinstance(source, Message):
            await source.answer(error_msg)
        else:
            await source.message.answer(error_msg)


async def safe_edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardBuilder] = None
):
    """Безопасное редактирование сообщения с обработкой ошибок"""
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup.as_markup() if reply_markup else None
        )
    except Exception as e:
        if "not modified" not in str(e):
            print(f"Error editing message: {e}")

async def format_transaction_details(transaction: Dict[str, Any]) -> str:
    """Форматирование данных транзакции"""
    return (
        "✏️ Редактирование транзакции:\n\n"
        f"1. 📁 Категория: {transaction.get('category_name', 'Без категории')}\n"
        f"2. 💰 Сумма: {float(transaction.get('full_sum', 0)):.2f} ₽\n"
        f"3. 📝 Описание: {transaction.get('description', 'Нет описания')}\n"
        f"4. 📅 Дата: {transaction.get('date', 'Не указана')[:10]}\n\n"
        "Выберите что изменить:"
    )






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
        await message.answer(
        "⬆️⬆️",
        reply_markup=ReplyKeyboardRemove()
    )
    except Exception as e:
        await message.answer(f"Ошибка при получении записи: {e}")

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
        
        await state.tdata(original_message=message_text)
        await callback.message.edit_text(text=message_text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        print(f"Ошибка пагинации: {e}")
        await callback.answer("Произошла ошибка, попробуйте позже")

@router.callback_query(F.data.startswith("select_transactionD_"))
async def handle_transaction_selection_for_delete(callback: CallbackQuery, state: FSMContext):
    transaction_id = int(callback.data.split('_')[2])
    transaction_name = str(callback.data.split('_')[3])
    await state.update_data(selected_transaction_id=transaction_id)
    await state.update_data(selected_transaction_name=transaction_name)

    # Получаем оригинальное сообщение
    data = await state.get_data()
    original_message = data.get('original_message', "Список записей")

    # Создание клавиатуры через билдер
    builder = await confirm_or_cancel_buttons()

    await callback.message.edit_text(
        text=f"{original_message}\n\n"
             f"Выбрана запись : '{transaction_name}'\n"
             "❗️Вы уверены, что хотите удалить эту запись?",
        reply_markup=builder.as_markup()
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
                reply_markup=await start_keyboard()
            )
            
    else:
        await callback.message.edit_text("⚠️ Ошибка: ID записи не найден.")

    await callback.answer()
    await state.clear()

@router.callback_query(F.data == "cancel_delete")
async def cancel_delete_transaction(callback: CallbackQuery, state: FSMContext):
    builder = await back_menu_or_list_transactions()
    await callback.message.answer("🙂 Хотите удалить другую запись или вернуться в главное меню?",
            reply_markup=builder.as_markup())
    await state.clear()

@router.callback_query(F.data == "back_to_menu")
async def cancel_delete_transaction(callback: CallbackQuery, state: FSMContext):
    builder = await back_menu_or_list_transactions()
    await callback.message.answer("🙂Мы вернулись в главное меню.",
            reply_markup=await start_keyboard())
    await state.clear()




@router.message(F.text == 'История моих записей')
async def show_transactions(message: Message):
    user_id = message.from_user.id
    user_pages[user_id] = 0  # Сбрасываем на первую страницу
    
    try:
        message_text, total_pages = await get_paginated_transactions(user_id, 0)
        keyboard = await build_pagination_keyboard_for_show(0, total_pages, user_id)
        await message.answer('📂 Вот список всех записей😊 :\n\n'+message_text, reply_markup=keyboard)
        await message.answer(
        "⬆️⬆️",
        reply_markup=ReplyKeyboardRemove()
    )
    except Exception as e:
        await message.answer(f"Ошибка при получении записи: {e}")

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
        print(f"Ошибка пагинации: {e}")
        await callback.answer(f"Произошла ошибка, попробуйте позже")

@router.callback_query(F.data == "show_cancel")
async def cancel_delete_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🙂Мы вернулись в главное меню.",
            reply_markup=await start_keyboard())
    await state.clear()