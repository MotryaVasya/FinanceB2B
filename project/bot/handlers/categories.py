from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from project.bot.conecting_methods.category import create_category, delete_category, get_categories, get_category, update_category
from project.bot.conecting_methods.methods import check_category_action
from project.bot.keyboards.inline_categories import (build_pagination_keyboard_for_delete, 
                                                     build_pagination_keyboard_for_show, 
                                                     build_pagination_keyboard_for_update, 
                                                     choose_buttons_delete, 
                                                     choose_buttons_update, 
                                                     confirm_back_cancel, 
                                                     confirm_or_cancel_buttons, 
                                                     income_expence_back_cancel)
from project.bot.states import *
from project.bot.messages.messages import *
from aiogram.fsm.context import FSMContext
from project.bot.keyboards.reply import *
from project.bot.messages.mesage_transaction import PAGE_SIZE, get_paginated_category, user_pages

def validate_name(name: str) -> bool:
    """
    Проверяет название по заданным правилам:
    1. Длина не более 50 символов
    2. Начинается с буквы или цифры
    3. Не содержит специальных символов @#$% и т.п.
    4. Не состоит только из цифр (должна быть хотя бы одна буква)
    
    :param name: Название для проверки
    :return: True если название валидно, False если нет
    """
    if len(name) == 0 or len(name) > 50:
        return False
    
    if not name[0].isalnum():
        return False
    
    for char in name:
        if not (char.isalnum() or char in (' ', '-', '_')):
            return False
    
    if all(char.isdigit() for char in name if char.isalnum()):
        return False
    
    if not any(char.isalpha() for char in name):
        return False
    
    return True

router = Router()

class CategoryForm(StatesGroup):
    name = State()
    type = State()
    confirmation = State() 

class UpdateCategoryForm(StatesGroup):
    select_category = State()
    new_name = State()
    new_type = State()
    confirmation = State()

# ----------------------------------------------------------- start add_category
@router.message(F.text == 'Добавить категорию')
async def start_add_category(message: Message, state: FSMContext):
    """Начало процесса создания категории"""
    await state.set_state(CategoryForm.name)
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="❌ Отмена", callback_data="cancel_creation")
    await message.answer(
        "💡 Введите название новой категории:\n"
        "\n"
        "❕ Пожалуйста, учтите требования:\n"
        "🔹 Не длиннее 50 символов\n"
        "🔹 Начинается с буквы или цифры\n"
        "🔹 Разрешены буквы, цифры, пробелы, дефисы и подчёркивания\n"  
        "🔹 Обязательно должна быть хотя бы одна буква\n"  
        "🔹 Не может состоять только из цифр\n"
        "\n"
        "✨ Придумайте понятное и короткое название — оно поможет вам быстрее ориентироваться в записях!\n",
        reply_markup=keyboard.as_markup()
    )
    # Затем отправляем сообщение с инлайн-клавиатурой
    await message.answer(
        "⬆️⬆️",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(CategoryForm.name)
async def process_name(message: Message, state: FSMContext):
    """Обработка названия категории и запрос типа"""
    name = message.text.strip()
    
    if not validate_name(name):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="❌ Отмена", callback_data="cancel_creation")
        await message.answer(
            "❌ Некорректное название категории. Пожалуйста, введите название, соответствующее требованиям:\n\n"
            "🔹 Не длиннее 50 символов\n"
            "🔹 Начинается с буквы или цифры\n"
            "🔹 Разрешены буквы, цифры, пробелы, дефисы и подчёркивания\n"  
            "🔹 Обязательно должна быть хотя бы одна буква\n"  
            "🔹 Не может состоять только из цифр\n",
            reply_markup=keyboard.as_markup()
        )
        return
    
    await state.update_data(name=name)
    await state.set_state(CategoryForm.type)
    
    keyboard = await income_expence_back_cancel()
    
    await message.answer(
        "🎉 Готово! Название категории добавлено. Пожалуйста, выберите тип:\n",
        reply_markup=keyboard.as_markup()
    )

@router.callback_query(F.data.startswith("type_"), CategoryForm.type)
async def process_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа и переход к подтверждению"""
    type_value = int(callback.data.split('_')[1])
    await state.update_data(type=type_value)
    await state.set_state(CategoryForm.confirmation)
    
    data = await state.get_data()
    category_type = "Доход" if type_value == 1 else "Расход"
    
    keyboard = await confirm_back_cancel()
    
    await callback.message.edit_text(
        f"Проверьте, пожалуйста, данные перед сохранением 💫\n\n"
        f"Название: {data['name']}\n"
        f"Тип: {category_type}\n\n"
        f"Всё верно?😊\n",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_creation", CategoryForm.confirmation)
async def confirm_creation(callback: CallbackQuery, state: FSMContext):
    """Финальное подтверждение и создание категории"""
    data = await state.get_data()
    user_id = callback.from_user.id
    
    try:
        category_data = {
            "name_category": data['name'],
            "type": data['type'],
        }
        
        await create_category(category_data, {"user_id": user_id})
        await callback.message.answer(
            f"✅ Категория успешно создана!\n\n"
            f"Название: {data['name']}\n"
            f"Тип: {'Доход' if data['type'] == 1 else 'Расход'}\n\n"
            f"🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка при создании категории: {e}\n"
            "Попробуйте еще раз, начиная с команды /add_category"
        )
    finally:
        await state.clear()
        await callback.answer()

@router.callback_query(F.data == "back_to_name")
async def back_to_name_step(callback: CallbackQuery, state: FSMContext):
    """Возврат к вводу названия категории"""
    await state.set_state(CategoryForm.name)
    data = await state.get_data()
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="❌ Отмена", callback_data="cancel_creation")
    
    await callback.message.edit_text(
        "💡 Введите название новой категории:\n"
        "\n"
        "❕ Пожалуйста, учтите требования:\n"
        "🔹 Не длиннее 50 символов\n"
        "🔹 Начинается с буквы или цифры\n"
        "🔹 Разрешены буквы, цифры, пробелы, дефисы и подчёркивания\n"  
        "🔹 Обязательно должна быть хотя бы одна буква\n"  
        "🔹 Не может состоять только из цифр\n"
        "\n"
        "✨ Придумайте понятное и короткое название — оно поможет вам быстрее ориентироваться в записях!\n",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_type", CategoryForm.confirmation)
async def back_to_type_step(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору типа категории"""
    await state.set_state(CategoryForm.type)
    
    keyboard = await income_expence_back_cancel()
    
    await callback.message.edit_text(
        "😊 Пожалуйста, выберите тип:",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_creation")
async def cancel_creation(callback: CallbackQuery, state: FSMContext):
    """Отмена создания категории"""
    await state.clear()
    await callback.message.answer("❌ Создание категории отменено", reply_markup=await start_keyboard())
    await callback.answer()
# ----------------------------------------------------------- end add_category

# ----------------------------------------------------------- start show_categories
@router.message(F.text == 'Посмотреть список существующих')
async def show_category(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user_pages[user_id] = 0  # Сбрасываем на первую страницу
    
    try:
        message_text, total_pages = await get_paginated_category(user_id, 0, True)
        keyboard = await build_pagination_keyboard_for_show(0, total_pages, user_id)
        await message.answer(message_text, reply_markup=keyboard)
        await message.answer(
        "⬆️⬆️",
        reply_markup=ReplyKeyboardRemove()
    )
    except Exception as e:
        await message.answer(f"Ошибка при получении категории: {e}")

@router.callback_query(F.data.startswith("categories_"))
async def handle_pagination_for_show(callback: CallbackQuery):
    try:
        data_parts = callback.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        current_page = user_pages.get(user_id, 0)
        all_categories = await get_categories(user_id)
        total_pages = (len(all_categories) + PAGE_SIZE - 1) // PAGE_SIZE
        
        # Определяем новую страницу
        new_page = await check_category_action(action, total_pages, current_page, callback)
        
        user_pages[user_id] = new_page
        message_text, total_pages = await get_paginated_category(user_id, new_page, True)
        keyboard = await build_pagination_keyboard_for_show(new_page, total_pages, user_id)
        
        await callback.message.edit_text(message_text, reply_markup=keyboard)
        await callback.answer()
    
    except Exception as e:
        print(f"Ошибка пагинации: {e}")
        await callback.answer("Произошла ошибка, попробуйте позже")

async def format_categories_page(categories: list, page: int) -> str:
    """Форматирует страницу с категориями для отображения (обновленная версия)"""
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
    header = "Вот ваш список категорий 📂:\n\n"
    message = header + "\n\n".join(formatted)
    message += f"\n\nСтраница {page + 1}/{total_pages}"
    
    return message

async def income_expence_back_cancel_keep():
    """Клавиатура для выбора типа с кнопкой 'Оставить как есть'"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Доход", callback_data="type_1")
    keyboard.button(text="Расход", callback_data="type_2")
    keyboard.button(text="◀ Назад", callback_data="back_to_name_update")
    keyboard.button(text="❌ Отмена", callback_data="cancel_update")
    keyboard.button(text="Оставить текущий", callback_data="keep_type")
    keyboard.adjust(2, 2, 1)
    return keyboard

async def confirm_back_cancel_for_update():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Подтвердить", callback_data="confirm_update")
    keyboard.button(text="✏️ Изменить тип", callback_data="back_to_type_update")
    keyboard.button(text="📝 Изменить название", callback_data="back_to_name_update")
    keyboard.button(text="❌ Отмена", callback_data="cancel_update")
    keyboard.adjust(2, 2)
    return keyboard
# ----------------------------------------------------------- end show_categories

# ----------------------------------------------------------- start update
@router.message(F.text == 'Изменить категорию')
async def start_update_category(message: Message, state: FSMContext):
    """Начало процесса обновления категории"""
    await state.clear()
    user_id = message.from_user.id
    user_pages[user_id] = 0  # Сбрасываем на первую страницу
    
    try:
        # Получаем только пользовательские категории (где есть user_id)
        all_categories = await get_categories(user_id)
        user_categories = [cat for cat in all_categories if cat.get('user_id')]
        
        # Сохраняем список категорий в state
        await state.update_data(all_categories=user_categories)
        
        # Получаем текст сообщения и клавиатуру для первой страницы
        message_text = await format_categories_page(user_categories, 0)
        total_pages = max(1, (len(user_categories) + PAGE_SIZE - 1) // PAGE_SIZE)
        keyboard = await build_pagination_keyboard_for_update(0, total_pages, user_id)
        
        await message.answer(message_text, reply_markup=keyboard)
        await message.answer(
            "⬆️⬆️",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        await message.answer(f"Ошибка при получении категорий: {e}")

@router.callback_query(F.data.startswith("categoryU_"))
async def handle_pagination_for_update(callback: CallbackQuery, state: FSMContext):
    """Обработка пагинации при обновлении категорий"""
    try:
        data_parts = callback.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        current_page = user_pages.get(user_id, 0)
        
        # Получаем сохраненный список категорий из state
        state_data = await state.get_data()
        user_categories = state_data.get('all_categories', [])
        total_pages = max(1, (len(user_categories) + PAGE_SIZE - 1) // PAGE_SIZE)
        
        # Обрабатываем действие (пагинация или выбор)
        if action == "choose":
            # Показываем кнопки выбора категорий на текущей странице
            start_idx = current_page * PAGE_SIZE
            page_categories = user_categories[start_idx:start_idx + PAGE_SIZE]
            
            keyboard = await choose_buttons_update(user_id, page_categories)
            await callback.message.edit_reply_markup(reply_markup=keyboard.as_markup())
            await callback.answer()
            return
            
        elif action == "back":
            # Возврат из режима выбора к пагинации
            await state.clear()
            message_text = await format_categories_page(user_categories, current_page)
            keyboard = await build_pagination_keyboard_for_update(current_page, total_pages, user_id)
            await callback.message.edit_text(text=message_text, reply_markup=keyboard)
            await callback.answer()
            return
            
        # Обработка пагинации
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
            
        if new_page != current_page:
            user_pages[user_id] = new_page
            message_text = await format_categories_page(user_categories, new_page)
            keyboard = await build_pagination_keyboard_for_update(new_page, total_pages, user_id)
            await callback.message.edit_text(text=message_text, reply_markup=keyboard)
            
        await callback.answer()
        
    except Exception as e:
        print(f"Error in handle_pagination_for_update: {e}")
        await callback.answer("Произошла ошибка при обработке")

@router.callback_query(F.data.startswith("select_categoryU_"))
async def select_category_for_update(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории для обновления"""
    try:
        data_parts = callback.data.split('_')
        category_id = int(data_parts[2])
        category_name = '_'.join(data_parts[3:])
        
        await state.update_data(
            category_id=category_id,
            current_name=category_name,
            original_message=callback.message.text
        )
        await state.set_state(UpdateCategoryForm.new_name)
        
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="◀ Назад", callback_data=f"categoryU_back_{callback.from_user.id}")
        keyboard.button(text="Оставить как есть", callback_data="keep_name")
        
        await callback.message.edit_text(
            text=f"Выбрана категория: {category_name}\n\n"
                 "Введите новое название категории ✏️\n"
                 'Или нажмите "Оставить как есть", если менять ничего не нужно\n'
                 ,
            reply_markup=keyboard.as_markup()
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Error in select_category_for_update: {e}")
        await callback.answer("Ошибка при выборе категории")

@router.callback_query(F.data == "keep_name", UpdateCategoryForm.new_name)
async def keep_current_name(callback: CallbackQuery, state: FSMContext):
    """Обработка сохранения текущего названия"""
    data = await state.get_data()
    await state.update_data(new_name=data['current_name'])
    await state.set_state(UpdateCategoryForm.new_type)
    
    keyboard = await income_expence_back_cancel_keep()
    await callback.message.edit_text(
        "Выберите новый тип категории 🔄\n"
        'Или нажмите "Оставить текущий", если менять ничего не нужно\n',
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@router.message(UpdateCategoryForm.new_name)
async def process_new_name(message: Message, state: FSMContext):
    """Обработка нового названия категории"""
    await state.update_data(new_name=message.text)
    await state.set_state(UpdateCategoryForm.new_type)
    
    keyboard = await income_expence_back_cancel_keep()
    await message.answer(
        "Выберите новый тип категории 🔄\n"
        'Или нажмите "Оставить текущий", если менять ничего не нужно\n',
        reply_markup=keyboard.as_markup()
    )

@router.callback_query(F.data.startswith("type_"), UpdateCategoryForm.new_type)
async def process_new_type(callback: CallbackQuery, state: FSMContext):
    """Обработка нового типа категории"""
    type_value = int(callback.data.split('_')[1])
    await state.update_data(new_type=type_value)
    await state.set_state(UpdateCategoryForm.confirmation)
    
    data = await state.get_data()
    category_type = "Доход" if type_value == 1 else "Расход"
    
    keyboard = await confirm_back_cancel_for_update()
    await callback.message.edit_text(
        f"Проверьте новые данные 🔍:\n\n"
        f"Текущее название: {data['current_name']}\n"
        f"Новое название: {data['new_name']}\n"
        f"Новый тип: {category_type}\n\n"
        f"Подтверждаете изменения? 😊",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "keep_type", UpdateCategoryForm.new_type)
async def keep_current_type(callback: CallbackQuery, state: FSMContext):
    """Обработка сохранения текущего типа"""
    data = await state.get_data()
    # Получаем текущий тип категории из базы данных
    category = await get_category(data['category_id'])
    await state.update_data(new_type=category['type'])
    await state.set_state(UpdateCategoryForm.confirmation)
    
    category_type = "Доход" if category['type'] == 1 else "Расход"
    
    keyboard = await confirm_back_cancel_for_update()
    await callback.message.edit_text(
        f"Проверьте новые данные 🔍:\n\n"
        f"Текущее название: {data['current_name']}\n"
        f"Новое название: {data['new_name']}\n"
        f"Тип остался без изменений: {category_type}\n\n"
        f"Подтверждаете изменения? 😊",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_type_update", UpdateCategoryForm.confirmation)
async def back_to_type_step_update(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору типа категории"""
    await state.set_state(UpdateCategoryForm.new_type)
    
    keyboard = await income_expence_back_cancel()
    await callback.message.edit_text(
        "😊 Пожалуйста, выберите тип:",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_name_update", UpdateCategoryForm.confirmation)
async def back_to_name_step_update(callback: CallbackQuery, state: FSMContext):
    """Возврат к вводу названия категории"""
    await state.set_state(UpdateCategoryForm.new_name)
    data = await state.get_data()
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="◀ Назад", callback_data=f"categoryU_back_{callback.from_user.id}")
    
    await callback.message.edit_text(
        f"Текущее название: {data.get('current_name', '')}\n"
        "Введите новое название категории ✏️",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_update", UpdateCategoryForm.confirmation)
async def confirm_update_category(callback: CallbackQuery, state: FSMContext):
    """Подтверждение обновления категории"""
    try:
        data = await state.get_data()
        update_data = {
            "name_category": data['new_name'],
            "type": data['new_type']
        }
        
        await update_category(data['category_id'], update_data)
        await callback.message.answer(
            text=f"✅ Категория успешно обновлена!\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
        await state.clear()
        await callback.answer()
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при обновлении: {e}\nПопробуйте снова"
        )
        await callback.answer()

@router.callback_query(F.data == "cancel_update")
async def cancel_update_category(callback: CallbackQuery, state: FSMContext):
    """Отмена обновления категории"""
    try:
        await callback.message.answer(
            text="❌ Обновление отменено\n\n",
            reply_markup=await start_keyboard()
        )
        await state.clear()
        await callback.answer()
        
    except Exception as e:
        print(f"Error in cancel_update_category: {e}")
        await callback.message.edit_text("❌ Обновление отменено")
        await state.clear()
        await callback.answer()
# ----------------------------------------------------------- end update

# ----------------------------------------------------------- start delete
@router.message(F.text == 'Удалить категорию')
async def start_delete_category(message: Message, state: FSMContext):
    """Начало процесса удаления категории"""
    await state.clear()
    user_id = message.from_user.id
    user_pages[user_id] = 0  # Сбрасываем на первую страницу
    
    try:
        # Получаем только пользовательские категории (где есть user_id)
        all_categories = await get_categories(user_id)
        user_categories = [cat for cat in all_categories if cat.get('user_id')]
        
        # Сохраняем список категорий в state
        await state.update_data(all_categories=user_categories)
        
        # Получаем текст сообщения и клавиатуру для первой страницы
        message_text = await format_categories_page(user_categories, 0)
        total_pages = max(1, (len(user_categories) + PAGE_SIZE - 1) // PAGE_SIZE)
        keyboard = await build_pagination_keyboard_for_delete(0, total_pages, user_id)
        
        await message.answer(message_text, reply_markup=keyboard)
        await message.answer(
        "⬆️⬆️",
        reply_markup=ReplyKeyboardRemove()
    )
    except Exception as e:
        await message.answer(f"Ошибка при получении категорий: {e}")

@router.callback_query(F.data.startswith("categoryD_"))
async def handle_pagination_for_delete(callback: CallbackQuery, state: FSMContext):
    """Обработка пагинации при удалении категорий"""
    try:
        data_parts = callback.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        current_page = user_pages.get(user_id, 0)
        
        # Получаем сохраненный список категорий из state
        state_data = await state.get_data()
        user_categories = state_data.get('all_categories', [])
        total_pages = max(1, (len(user_categories) + PAGE_SIZE - 1) // PAGE_SIZE)
        
        # Обрабатываем действие (пагинация или выбор)
        if action == "choose":
            # Показываем кнопки выбора категорий на текущей странице
            start_idx = current_page * PAGE_SIZE
            page_categories = user_categories[start_idx:start_idx + PAGE_SIZE]
            
            keyboard = await choose_buttons_delete(user_id, page_categories)
            await callback.message.edit_reply_markup(reply_markup=keyboard.as_markup())
            await callback.answer()
            return
            
        elif action == "back":
            # Возврат из режима выбора к пагинации
            message_text = await format_categories_page(user_categories, current_page)
            keyboard = await build_pagination_keyboard_for_delete(current_page, total_pages, user_id)
            await callback.message.edit_text(text=message_text, reply_markup=keyboard)
            await callback.answer()
            return
            
        # Обработка пагинации
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
            
        if new_page != current_page:
            user_pages[user_id] = new_page
            message_text = await format_categories_page(user_categories, new_page)
            keyboard = await build_pagination_keyboard_for_delete(new_page, total_pages, user_id)
            await callback.message.edit_text(text=message_text, reply_markup=keyboard)
            
        await callback.answer()
        
    except Exception as e:
        print(f"Error in handle_pagination_for_delete: {e}")
        await callback.answer("Произошла ошибка при обработке")

@router.callback_query(F.data.startswith("select_categoryD_"))
async def select_category_for_delete(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора конкретной категории для удаления"""
    try:
        data_parts = callback.data.split('_')
        category_id = int(data_parts[2])
        category_name = '_'.join(data_parts[3:])  # Восстанавливаем название
        
        # Декодируем название из callback_data
        try:
            category_name = category_name.encode('utf-8').decode('utf-8')
        except:
            pass
            
        await state.update_data(
            category_id=category_id,
            category_name=category_name,
            original_message=callback.message.text
        )
        
        keyboard = await confirm_or_cancel_buttons()
        await callback.message.edit_text(
            text=f"Вы уверены, что хотите удалить категорию?\n\n"
                 f"🔖 {category_name}\n\n"
                 f'Все связанные транзакции будут перемещены в категорию "Без категории"?\n'
                 f"😊 Подтвердите действие, если всё верно!",
            reply_markup=keyboard.as_markup()
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Error in select_category_for_delete: {e}")
        await callback.answer("Ошибка при выборе категории")

@router.callback_query(F.data == "confirm_delete_category")
async def confirm_delete_category(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления категории"""
    try:
        data = await state.get_data()
        user_id = callback.from_user.id
        
        await delete_category(data['category_id'])
        
        # Обновляем список категорий после удаления
        all_categories = await get_categories(user_id)
        user_categories = [cat for cat in all_categories if cat.get('user_id')]
        await state.update_data(all_categories=user_categories)
        
        
        await callback.message.answer(
            text=f"✅ Категория '{data['category_name']}' успешно удалена!\n"
            "🔙 Возвращаемся в главное меню!\n\n",
            reply_markup=await start_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при удалении категории: {e}\n\n"
            "Попробуйте снова или обратитесь к администратору"
        )
        await callback.answer()

@router.callback_query(F.data == "cancel_delete_category")
async def cancel_delete_category(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления категории"""
    try:
        await callback.message.answer(
            text="❌ Удаление отменено\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
        await callback.answer()
        await state.clear()
    except Exception as e:
        print(f"Error in cancel_delete_category: {e}")
        await callback.message.edit_text("❌ Удаление отменено")
        await callback.answer()
# ----------------------------------------------------------- start delete

@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.answer(
            text="❌ Вы вернулись в меню.\n"
            "Можете выбрать нужный раздел и продолжить работу 😊\n\n",
            reply_markup=await start_keyboard()
        )
        await state.clear()
        await callback.answer()
    
    except Exception as e:
        print(f"Error in cancel_update_category: {e}")
        await callback.message.edit_text("❌ Обновление отменено")
        await state.clear()
        await callback.answer()