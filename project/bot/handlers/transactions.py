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

from project.bot.conecting_methods.transactions import create_transaction, delete_transaction, get_transactions
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

@router.message(F.text == 'add transaction')
async def add_transaction_start(message: Message, state: FSMContext):
    # Получаем список категорий пользователя
    categories = await get_categories(message.from_user.id)
    
    if not categories:
        await message.answer("У вас нет категорий. Сначала создайте хотя бы одну категорию.")
        return
    
    # Создаем клавиатуру с категориями
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category['name_category'],
            callback_data=f"addtx_category_{category['id']}"
        )
    builder.button(text="❌ Отмена", callback_data="addtx_cancel")
    builder.adjust(2)
    
    await state.set_state(AddTransaction.waiting_for_category)
    await message.answer(
        "Выберите категорию для новой транзакции:",
        reply_markup=builder.as_markup()
    )

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

@router.message(AddTransaction.waiting_for_date)
async def set_custom_date(message: Message, state: FSMContext):
    try:
        date_str = message.text.strip()
        datetime.strptime(date_str, "%Y-%m-%d")  # Проверка формата
        await state.update_data(date=date_str)
        await show_confirmation(message, state)
    except ValueError:
        await message.answer("Некорректный формат даты. Введите в формате ГГГГ-ММ-ДД (например: 2023-12-31):")

async def show_confirmation(update: Union[Message, CallbackQuery], state: FSMContext):
    data = await state.get_data()
    
    # Формируем сообщение с данными
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










@router.message(or_f(F.text == "Изменить запись",F.text=="Пропустить изменение категории"))
async def update_transaction_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        await state.set_state(TransactionStates.in_update_name)
        open("add_handler.txt", "w").write(str(await save.update(user_id, "ADD_TRANSACTION")))
        open("main44.txt", "w").write(str(await save.convert_to_json()))
        await message.answer(
            "🎉 Вот все ваши записи! Какую вы хотите изменить?\n"
            "1. название записи\n"
            "2. название записи\n"
            "итп\n",
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(TransactionStates.in_update_name)
async def del_after_choos1(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.in_update_cat)
        await message.answer(
            "✨ Выберите новую категорию, пожалуйста!\n\
            1. название\n\
            2. название\n\
            итп.\n",
            reply_markup= await skip_update_from_trans()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")


@router.message(TransactionStates.in_update_cat)
async def del_after_choos2(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.update_for_transaction_description)
        await message.answer(
            "📝 Введите описание для вашей записи (или пропустите):\n",
            reply_markup= await skip_update_desk_from_trans()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")


@router.message(F.text=="Пропустить описание записи")
async def del_after_choos3(message: Message, state: FSMContext):
    try:
        name = message.text.strip()
        avtobus[0]=name
        await state.set_state(TransactionStates.update_for_transaction_amount)
        await message.answer(
            "🎉Измените сумму вашей записи:\n",
            reply_markup= await skip_update_amount_from_trans()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")
@router.message(TransactionStates.update_for_transaction_description)
async def del_after_choos4(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.update_for_transaction_amount)
        await message.answer(
            "🎉Измените сумму вашей записи:\n",
            reply_markup= await skip_update_amount_from_trans()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(F.text=="Пропустить изменение суммы")
async def del_after_choos5(message: Message, state: FSMContext):
    try:
        name = message.text.strip()
        avtobus[1]=name
        await state.set_state(TransactionStates.wait_date_update)
        await message.answer(
            "Ура!Теперь измени дату 📅😊\n",
            reply_markup= await from_trans_skip_or_date()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(TransactionStates.update_for_transaction_amount)
async def del_after_choos6(message: Message, state: FSMContext):
    name = message.text.strip()
    try:
        await state.set_state(TransactionStates.wait_date_update)
        if(name.isdigit()):
            await message.answer(
                "Ура! 🎉 Ты успешно добавил сумму! Теперь измени дату 📅😊\n",
                reply_markup= await from_trans_skip_or_date()
            )
        else:
            await message.answer(
                text_no
            )
            return
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")
@router.message(or_f(TransactionStates.wait_date_update,F.text=="Пропустить изменение даты"))
async def after_date_update(message: Message, state: FSMContext):
    name = message.text.strip()
    avtobus[2]=name
    try:
        if(avtobus[0]=="Пропустить описание записи" and avtobus[1]=="Пропустить изменение суммы" and avtobus[2]=="Пропустить изменение даты"):
            await state.set_state(TransactionStates.update_no_sets)
            await message.answer(
                "😕 Ничего не изменилось.\n Хотите вернуться и попробовать снова или оставить всё как есть?\n",
                reply_markup= await aboba_keyboard()
            )
        else:
            await state.clear()
            await message.answer(
                "🎉 Отлично! Я сохранил вашу запись😊\n"
                "🔙 Возвращаемся в главное меню!\n",
                reply_markup=await start_keyboard()
            )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(or_f(StateFilter(TransactionStates.update_no_sets),F.text == "Оставить как есть"))
async def set_type(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer(
            "👌 Всё оставлено как есть! Если что-то нужно будет изменить, я всегда готов помочь 😊\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
    except Exception as e:
            print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")







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
    transaction_name = str(callback.data.split('_')[3])
    await state.update_data(selected_transaction_id=transaction_id)
    await state.update_data(selected_transaction_name=transaction_name)

    # Получаем оригинальное сообщение
    data = await state.get_data()
    original_message = data.get('original_message', "Список транзакций")

    # Создание клавиатуры через билдер
    builder = await confirm_or_cancel_buttons()

    await callback.message.edit_text(
        text=f"{original_message}\n\n"
             f"Выбрана транзакция : '{transaction_name}'\n"
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
