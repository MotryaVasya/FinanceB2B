from aiogram.utils.keyboard import InlineKeyboardBuilder

from project.bot.messages.mesage_transaction import PAGE_SIZE

async def build_pagination_keyboard_for_show(page: int, total_pages: int, user_id: int):
    builder = InlineKeyboardBuilder()
    
    # Основные кнопки навигации
    if page > 0:
        builder.button(text="<", callback_data=f"transactions_prev_{user_id}")  # На 1 назад
    
    if page < total_pages - 1:
        builder.button(text=">", callback_data=f"transactions_next_{user_id}")  # На 1 вперед
    
    if page >= 1:  # Если не на первой странице
        if page >= 5:
            builder.button(text="<<", callback_data=f"transactions_back5_{user_id}")  # На 5 назад
        else:
            builder.button(text="<<", callback_data=f"transactions_first_{user_id}")  # В начало
    
    if page < total_pages - 1:  # Если не на последней странице
        if page + 5 < total_pages:
            builder.button(text=">>", callback_data=f"transactions_forward5_{user_id}")  # На 5 вперед
        else:
            builder.button(text=">>", callback_data=f"transactions_last_{user_id}")  # В конец

    builder.adjust(2, 2)
    return builder.as_markup()

async def build_pagination_keyboard_for_update(page: int, total_pages: int, user_id: int):
    builder = InlineKeyboardBuilder()
    
    # Основные кнопки навигации
    if page > 0:
        builder.button(text="<", callback_data=f"transactionU_prev_{user_id}")  # На 1 назад
    
    builder.button(text="Выбрать страницу", callback_data=f"transactionU_choose_{user_id}")
    
    if page < total_pages - 1:
        builder.button(text=">", callback_data=f"transactionU_next_{user_id}")  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if page >= 1:  # Если не на первой странице
        if page >= 5:
            builder.button(text="<<", callback_data=f"transactionU_back5_{user_id}")  # На 5 назад
        else:
            builder.button(text="<<", callback_data=f"transactionU_first_{user_id}")  # В начало
    
    if page < total_pages - 1:  # Если не на последней странице
        if page + 5 < total_pages:
            builder.button(text=">>", callback_data=f"transactionU_forward5_{user_id}")  # На 5 вперед
        else:
            builder.button(text=">>", callback_data=f"transactionU_last_{user_id}")  # В конец

    builder.adjust(3, 2)
    return builder.as_markup()

from aiogram.utils.keyboard import InlineKeyboardBuilder

async def build_pagination_keyboard_for_categories(page: int, total_pages: int, user_id: int):
    """Клавиатура пагинации для текстового списка категорий"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки пагинации
    if total_pages > 1:
        if page > 0:
            builder.button(text="<", callback_data=f"tx_categories_prev_{user_id}")
        if page < total_pages - 1:
            builder.button(text=">", callback_data=f"tx_categories_next_{user_id}")
        if page >= 5:
            builder.button(text="<<", callback_data=f"tx_categories_back5_{user_id}")
        if page + 5 < total_pages:
            builder.button(text=">>", callback_data=f"tx_categories_forward5_{user_id}")
        if page != 0:
            builder.button(text="<<", callback_data=f"tx_categories_first_{user_id}")
        if page != total_pages - 1:
            builder.button(text=">>", callback_data=f"tx_categories_last_{user_id}")
    
    builder.button(text="Выбрать категорию", callback_data=f"tx_categories_choose_{user_id}")
    builder.button(text="❌ Отмена", callback_data="addtx_cancel")
    
    builder.adjust(2, 2, 2, 2)  # Оптимальное расположение кнопок
    return builder.as_markup()

async def build_category_choice_keyboard(categories: list, user_id: int):
    """Клавиатура с кнопками категорий для выбора"""
    builder = InlineKeyboardBuilder()
    
    for category in categories:
        builder.button(
            text=category['name_category'],
            callback_data=f"addtx_category_{category['id']}"
        )
    
    builder.button(text="< Назад", callback_data=f"tx_categories_back_{user_id}")
    builder.button(text="❌ Отмена", callback_data="addtx_cancel")
    
    builder.adjust(2)  # По 2 кнопки в ряд
    return builder.as_markup()

async def build_pagination_keyboard_for_delete(page: int, total_pages: int, user_id: int):
    builder = InlineKeyboardBuilder()
    
    # Основные кнопки навигации
    if page > 0:
        builder.button(text="<", callback_data=f"transactionD_prev_{user_id}")  # На 1 назад
    
    builder.button(text="Выбрать страницу", callback_data=f"transactionD_choose_{user_id}")
    
    if page < total_pages - 1:
        builder.button(text=">", callback_data=f"transactionD_next_{user_id}")  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if page >= 1:  # Если не на первой странице
        if page >= 5:
            builder.button(text="<<", callback_data=f"transactionD_back5_{user_id}")  # На 5 назад
        else:
            builder.button(text="<<", callback_data=f"transactionD_first_{user_id}")  # В начало
    
    if page < total_pages - 1:  # Если не на последней странице
        if page + 5 < total_pages:
            builder.button(text=">>", callback_data=f"transactionD_forward5_{user_id}")  # На 5 вперед
        else:
            builder.button(text=">>", callback_data=f"transactionD_last_{user_id}")  # В конец

    builder.adjust(3, 2)
    return builder.as_markup()




async def choose_buttons_delete(user_id, page_transactions):
    builder = InlineKeyboardBuilder()
    for tx in page_transactions:
        tx_text = f"🔖 {tx['category_name']} | {tx['full_sum']:.2f} ₽ | 📅 {tx['date'][:10]}"
        builder.button(text=tx_text, callback_data=f"select_transactionD_{tx['id']}_{tx['description']}")
            
    builder.button(text="◀ Назад", callback_data=f"transactionD_back_{user_id}")
    builder.adjust(1)
    return builder

async def choose_buttons_update(user_id, page_transactions):
    builder = InlineKeyboardBuilder()
    for tx in page_transactions:
        tx_text = f"🔖 {tx['category_name']} | {tx['full_sum']:.2f} ₽ | 📅 {tx['date'][:10]}"
        builder.button(text=tx_text, callback_data=f"select_transactionU_{tx['id']}_{tx['description']}")
            
    builder.button(text="◀ Назад", callback_data=f"transactionU_back_{user_id}")
    builder.adjust(1)
    return builder

async def confirm_or_cancel_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data=f"confirm_delete")
    builder.button(text="❌ Нет", callback_data="cancel_delete")
    builder.adjust(2) 
    return builder

async def back_menu_or_list_transactions():
    builder = InlineKeyboardBuilder()
    builder.button(text='Вернутся к списку ваших записей', callback_data='back_to_list_transactions')
    builder.button(text='Вернутся к меню', callback_data='back_to_menu')
    return builder

async def retry_or_cancel_keyboard():
    """Клавиатура для повторной попытки или отмены"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Попробовать снова", callback_data="retry_update")
    builder.button(text="❌ Отменить", callback_data="cancel_update")
    return builder

async def confirm_changes_keyboard():
    """Клавиатура для подтверждения изменений"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="confirm_changes")
    builder.button(text="❌ Отменить", callback_data="cancel_update")
    return builder

