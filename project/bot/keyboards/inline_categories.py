from aiogram.utils.keyboard import InlineKeyboardBuilder

async def income_expence_back_cancel():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Доход", callback_data="type_1")
    keyboard.button(text="Расход", callback_data="type_0")
    keyboard.button(text="◀ Назад", callback_data="back_to_name")
    keyboard.button(text="❌ Отмена", callback_data="cancel_creation")
    keyboard.adjust(2, 2)
    return keyboard

async def confirm_back_cancel():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Подтвердить", callback_data="confirm_creation")
    keyboard.button(text="◀ Изменить тип", callback_data="back_to_type")
    keyboard.button(text="❌ Отмена", callback_data="cancel_creation")
    keyboard.adjust(2, 1)
    return keyboard

async def build_pagination_keyboard_for_show(page: int, total_pages: int, user_id: int):
    builder = InlineKeyboardBuilder()
    
    # Основные кнопки навигации
    if page > 0:
        builder.button(text="<", callback_data=f"categories_prev_{user_id}")  # На 1 назад
    
    if page < total_pages - 1:
        builder.button(text=">", callback_data=f"categories_next_{user_id}")  # На 1 вперед
    
    if page >= 1:  # Если не на первой странице
        if page >= 5:
            builder.button(text="<<", callback_data=f"categories_back5_{user_id}")  # На 5 назад
        else:
            builder.button(text="<<", callback_data=f"categories_first_{user_id}")  # В начало
    
    if page < total_pages - 1:  # Если не на последней странице
        if page + 5 < total_pages:
            builder.button(text=">>", callback_data=f"categories_forward5_{user_id}")  # На 5 вперед
        else:
            builder.button(text=">>", callback_data=f"categories_last_{user_id}")  # В конец

    builder.adjust(2, 2)
    return builder.as_markup()

async def choose_buttons_delete(user_id, page_categories):
    builder = InlineKeyboardBuilder()
    for category in page_categories:
        try:
            # Убедимся, что имя категории в UTF-8
            name = category['name_category'].encode('utf-8', errors='replace').decode('utf-8')
            category_type = "Доход" if category['type'] == 1 else "Расход"
            btn_text = f"{name} | {category_type}"
            
            builder.button(
                text=btn_text,
                callback_data=f"select_categoryD_{category['id']}_{name}"
            )
        except Exception as e:
            print(f"Error creating button for category: {e}")
            continue
            
    builder.button(text="◀ Назад", callback_data=f"categoryD_back_{user_id}")
    builder.adjust(1)
    return builder

async def choose_buttons_update(user_id, page_categories):
    builder = InlineKeyboardBuilder()
    for tx in page_categories:
        tx_text = f"🔖 {tx['name_category']} | {tx['type']}"
        builder.button(text=tx_text, callback_data=f"select_categoryU_{tx['id']}_{tx['name_category']}")
            
    builder.button(text="◀ Назад", callback_data=f"categoryU_back_{user_id}")
    builder.adjust(1)
    return builder

async def build_pagination_keyboard_for_update(page: int, total_pages: int, user_id: int):
    builder = InlineKeyboardBuilder()
    
    # Основные кнопки навигации
    if page > 0:
        builder.button(text="<", callback_data=f"categoryU_prev_{user_id}")  # На 1 назад
    
    builder.button(text="Выбрать страницу", callback_data=f"categoryU_choose_{user_id}")
    
    if page < total_pages - 1:
        builder.button(text=">", callback_data=f"categoryU_next_{user_id}")  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if page >= 1:  # Если не на первой странице
        if page >= 5:
            builder.button(text="<<", callback_data=f"categoryU_back5_{user_id}")  # На 5 назад
        else:
            builder.button(text="<<", callback_data=f"categoryU_first_{user_id}")  # В начало
    
    if page < total_pages - 1:  # Если не на последней странице
        if page + 5 < total_pages:
            builder.button(text=">>", callback_data=f"categoryU_forward5_{user_id}")  # На 5 вперед
        else:
            builder.button(text=">>", callback_data=f"categoryU_last_{user_id}")  # В конец

    builder.adjust(3, 2)
    return builder.as_markup()

async def build_pagination_keyboard_for_delete(page: int, total_pages: int, user_id: int):
    builder = InlineKeyboardBuilder()
    
    # Основные кнопки навигации
    if page > 0:
        builder.button(text="<", callback_data=f"categoryD_prev_{user_id}")  # На 1 назад
    
    builder.button(text="Выбрать страницу", callback_data=f"categoryD_choose_{user_id}")
    
    if page < total_pages - 1:
        builder.button(text=">", callback_data=f"categoryD_next_{user_id}")  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if page >= 1:  # Если не на первой странице
        if page >= 5:
            builder.button(text="<<", callback_data=f"categoryD_back5_{user_id}")  # На 5 назад
        else:
            builder.button(text="<<", callback_data=f"categoryD_first_{user_id}")  # В начало
    
    if page < total_pages - 1:  # Если не на последней странице
        if page + 5 < total_pages:
            builder.button(text=">>", callback_data=f"categoryD_forward5_{user_id}")  # На 5 вперед
        else:
            builder.button(text=">>", callback_data=f"categoryD_last_{user_id}")  # В конец

    builder.adjust(3, 2)
    return builder.as_markup()


async def confirm_or_cancel_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data=f"confirm_delete_category")
    builder.button(text="❌ Нет", callback_data="cancel_delete_category")
    builder.adjust(2) 
    return builder