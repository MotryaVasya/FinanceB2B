from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup


# Убедитесь, что PAGE_SIZE импортируется корректно
# from project.bot.messages.mesage_transaction import PAGE_SIZE # Может быть определен в другом месте
# Если PAGE_SIZE определен в mesage_transaction.py, убедитесь, что этот импорт верен.
# Если PAGE_SIZE используется только здесь, определите его прямо тут, например:
PAGE_SIZE = 10 # Примерное значение

# Эта функция, кажется, используется только для просмотра, но добавлю as_markup() на всякий случай
async def build_pagination_keyboard_for_show(page: int, total_pages: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    total_pages = max(1, total_pages) # Убедимся, что страниц хотя бы 1

    # Основные кнопки навигации
    if page > 0:
        builder.button(text="<", callback_data=f"transactions_prev_{user_id}")  # На 1 назад

    if total_pages > 1: # Показываем номер страницы только если страниц больше одной
         builder.button(text=f"{page + 1}/{total_pages}", callback_data="ignore_page_number") # Не делаем колбэк кнопке с номером страницы

    if page < total_pages - 1:
        builder.button(text=">", callback_data=f"transactions_next_{user_id}")  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if total_pages > 1: # Показываем эти кнопки только если страниц больше одной
        if page > 0: # Только если не на первой странице
            if page >= 5:
                builder.button(text="<<", callback_data=f"transactions_back5_{user_id}")  # На 5 назад
            else: # Если нельзя на 5 назад, но не на первой
                 builder.button(text="<<", callback_data=f"transactions_first_{user_id}")  # В начало

        if page < total_pages - 1: # Только если не на последней странице
            if page + 5 < total_pages:
                builder.button(text=">>", callback_data=f"transactions_forward5_{user_id}")  # На 5 вперед
            else:
                 if page < total_pages -1 : # Только если не на последней странице
                    builder.button(text=">>", callback_data=f"transactions_last_{user_id}")  # В конец


    # Уберем лишние adjust вызовы, оставим один в конце
    # builder.adjust(2, 2)

    # Корректировка расположения
    # Сначала основные стрелки (3 кнопки), затем << >> (2 кнопки)
    adjust_rows = [3]
    if total_pages > 1: # Только если есть пагинация
         # Добавляем ряд с << и >> только если они отображаются (т.е. total_pages > 1 и есть движение более чем на 1)
         # Если total_pages > 5, то << и >> - это back5/forward5
         # Если total_pages <= 5, но > 1, то << и >> - это first/last
         # В любом случае, если total_pages > 1 и есть кнопки >>, <<, то их 2
         if page > 0 or page < total_pages -1: # Если есть хоть какое-то движение возможно
              adjust_rows.append(2) # Ряд с << и >> или << и >>


    builder.adjust(*adjust_rows)

    return builder.as_markup()


# Эта функция используется для пагинации в режиме ИЗМЕНЕНИЯ
async def build_pagination_keyboard_for_update(page: int, total_pages: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    total_pages = max(1, total_pages) # Убедимся, что страниц хотя бы 1

    # Основные кнопки навигации
    if page > 0:
        builder.button(text="<", callback_data=f"transactionU_prev_{user_id}")  # На 1 назад

    # Кнопка выбора - всегда ведет к списку на текущей странице
    builder.button(text="Выбрать запись", callback_data=f"transactionU_choose_{user_id}")

    if page < total_pages - 1:
        builder.button(text=">", callback_data=f"transactionU_next_{user_id}")  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if total_pages > 1: # Показываем эти кнопки только если страниц больше одной
        if page > 0: # Только если не на первой странице
            if page >= 5:
                builder.button(text="<<", callback_data=f"transactionU_back5_{user_id}")  # На 5 назад
            else: # Если нельзя на 5 назад, но не на первой
                 builder.button(text="<<", callback_data=f"transactionU_first_{user_id}")  # В начало

        if page < total_pages - 1: # Только если не на последней странице
            if page + 5 < total_pages:
                builder.button(text=">>", callback_data=f"transactionU_forward5_{user_id}")  # На 5 вперед
            else:
                 builder.button(text=">>", callback_data=f"transactionU_last_{user_id}")  # В конец


    # Корректировка расположения
    # Сначала основные стрелки (3 кнопки), затем << >> (2 кнопки)
    adjust_rows = [3]
    if total_pages > 1: # Только если есть пагинация
         # Добавляем ряд с << и >> только если они отображаются
         if page > 0 or page < total_pages - 1:
              adjust_rows.append(2)


    builder.adjust(*adjust_rows)

    return builder.as_markup()

# Эта функция используется для пагинации в режиме УДАЛЕНИЯ
async def build_pagination_keyboard_for_delete(page: int, total_pages: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    total_pages = max(1, total_pages) # Убедимся, что страниц хотя бы 1 

    # Основные кнопки навигации
    if page > 0:
        builder.button(text="<", callback_data=f"transactionD_prev_{user_id}")  # На 1 назад

    # Кнопка выбора - всегда ведет к списку на текущей странице
    builder.button(text="Выбрать запись", callback_data=f"transactionD_choose_{user_id}")

    if page < total_pages - 1:
        builder.button(text=">", callback_data=f"transactionD_next_{user_id}")  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if total_pages > 1: # Показываем эти кнопки только если страниц больше одной
        if page > 0: # Только если не на первой странице
            if page >= 5:
                builder.button(text="<<", callback_data=f"transactionD_back5_{user_id}")  # На 5 назад
            else: # Если нельзя на 5 назад, но не на первой
                 builder.button(text="<<", callback_data=f"transactionD_first_{user_id}")  # В начало

        if page < total_pages - 1: # Только если не на последней странице
            if page + 5 < total_pages:
                builder.button(text=">>", callback_data=f"transactionD_forward5_{user_id}")  # На 5 вперед
            else:
                 builder.button(text=">>", callback_data=f"transactionD_last_{user_id}")  # В конец


    # Корректировка расположения
    # Сначала основные стрелки (3 кнопки), затем << >> (2 кнопки)
    adjust_rows = [3]
    if total_pages > 1: # Только если есть пагинация
         # Добавляем ряд с << и >> только если они отображаются
         if page > 0 or page < total_pages - 1:
              adjust_rows.append(2)

    builder.adjust(*adjust_rows)

    return builder.as_markup()


# Клавиатура пагинации для текстового списка категорий
async def build_pagination_keyboard_for_categories(page: int, total_pages: int, user_id: int, prefix: str = "tx_categories_") -> InlineKeyboardMarkup: # Добавляем prefix
    """Клавиатура пагинации для текстового списка категорий"""
    builder = InlineKeyboardBuilder()

    total_pages = max(1, total_pages) # Убедимся, что страниц хотя бы 1

    # Кнопки пагинации
    if total_pages > 1:
        # Убедимся, что кнопки появляются только если есть куда двигаться
        # Кнопки Назад (<, <<, Первая)
        if page > 0:
            builder.button(text="⬅️", callback_data=f"{prefix}prev_{user_id}") # Используем prefix
            if page >= 5: # Если можно вернуться на 5 страниц назад
                 builder.button(text="⏪", callback_data=f"{prefix}back5_{user_id}") # Используем prefix
            else: # Если нельзя на 5 назад, но не на первой
                 builder.button(text="⏮", callback_data=f"{prefix}first_{user_id}") # Используем prefix

        # Кнопки Вперед (>, >>, Последняя)
        if page < total_pages - 1:
            builder.button(text="➡️", callback_data=f"{prefix}next_{user_id}") # Используем prefix
            if page + 5 < total_pages:
                 builder.button(text="⏩", callback_data=f"{prefix}forward5_{user_id}") # Используем prefix
            else:
                 builder.button(text="⏭", callback_data=f"{prefix}last_{user_id}") # Используем prefix


    # Кнопка Выбрать категорию
    builder.button(text="Выбрать категорию", callback_data=f"{prefix}choose_{user_id}") # Используем prefix

    # Кнопка Назад/Отмена в зависимости от префикса
    # В режиме добавления используем Отмена, в режиме редактирования - Назад к меню подтверждения
    if prefix == "tx_categories_":
        builder.button(text="❌ Отмена", callback_data="addtx_cancel")
        adjust_rows_bottom = [2] # Выбрать, Отмена
    else: # Предполагаем, что любой другой префикс используется в режиме редактирования
         # Добавляем кнопку Назад к меню подтверждения обновления
         builder.button(text="◀ Назад", callback_data="update_cat_back_to_confirm") # Этот callback нужно будет обработать в transactions.py
         adjust_rows_bottom = [1] # Назад


    # Корректировка расположения кнопок пагинации и нижних кнопок
    pagination_row_buttons_count = 0
    if total_pages > 1:
        if page > 0: pagination_row_buttons_count += (2 if page >= 5 else 2)
        if page < total_pages - 1: pagination_row_buttons_count += (2 if page + 5 < total_pages else 2)

    adjust_rows = []
    if pagination_row_buttons_count > 0:
        adjust_rows.append(pagination_row_buttons_count) # Ряд со стрелками пагинации

    # Ряд с кнопкой "Выбрать категорию"
    adjust_rows.append(1)

    # Ряд с кнопками "Назад"/"Отмена"
    adjust_rows.extend(adjust_rows_bottom)

    builder.adjust(*adjust_rows)
    return builder.as_markup()


# Клавиатура с кнопками категорий для выбора
async def build_category_choice_keyboard(categories: list, user_id: int) -> InlineKeyboardMarkup: # Убран prefix: str = "addtx_category_" здесь
    """Клавиатура с кнопками категорий для выбора"""
    builder = InlineKeyboardBuilder()

    for category in categories:
        # Используем префикс "addtx_category_" по умолчанию
        builder.button(
            text=category['name_category'],
            callback_data=f"addtx_category_{category['id']}"
        )

    # Кнопка Назад - возвращает к пагинации категорий добавления
    builder.button(text="◀ Назад", callback_data=f"tx_categories_back_{user_id}")
    # Кнопка Отмена для режима добавления
    builder.button(text="❌ Отмена", callback_data="addtx_cancel")


    # Расположение: кнопки категорий по 2 в ряд, затем Назад и Отмена в отдельном ряду
    adjust_rows = [2] * (len(categories) // 2) # По 2 кнопки категорий в ряд
    if len(categories) % 2 != 0:
        adjust_rows.append(1) # Если осталась одна кнопка категории
    adjust_rows.append(2) # Назад и Отмена в последнем ряду

    builder.adjust(*adjust_rows)
    return builder.as_markup()


# Эта функция используется для пагинации в режиме УДАЛЕНИЯ
async def build_pagination_keyboard_for_delete(page: int, total_pages: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    total_pages = max(1, total_pages) # Убедимся, что страниц хотя бы 1

    # Основные кнопки навигации
    if page > 0:
        builder.button(text="<", callback_data=f"transactionD_prev_{user_id}")  # На 1 назад

    # Кнопка выбора - всегда ведет к списку на текущей странице
    builder.button(text="Выбрать запись", callback_data=f"transactionD_choose_{user_id}")

    if page < total_pages - 1:
        builder.button(text=">", callback_data=f"transactionD_next_{user_id}")  # На 1 вперед

    # Кнопки для перехода на 5 страниц или в крайние положения
    if total_pages > 1: # Показываем эти кнопки только если страниц больше одной
        if page > 0: # Только если не на первой странице
            if page >= 5:
                builder.button(text="<<", callback_data=f"transactionD_back5_{user_id}")  # На 5 назад
            else: # Если нельзя на 5 назад, но не на первой
                 builder.button(text="<<", callback_data=f"transactionD_first_{user_id}")  # В начало

        if page < total_pages - 1: # Только если не на последней странице
            if page + 5 < total_pages:
                builder.button(text=">>", callback_data=f"transactionD_forward5_{user_id}")  # На 5 вперед
            else:
                 builder.button(text=">>", callback_data=f"transactionD_last_{user_id}")  # В конец


    # Корректировка расположения
    # Сначала основные стрелки (3 кнопки), затем << >> (2 кнопки)
    adjust_rows = [3]
    if total_pages > 1: # Только если есть пагинация
         # Добавляем ряд с << и >> только если они отображаются
         if page > 0 or page < total_pages - 1:
              adjust_rows.append(2)

    builder.adjust(*adjust_rows)

    return builder.as_markup()




async def choose_buttons_delete(user_id, page_transactions):
    builder = InlineKeyboardBuilder()
    for tx in page_transactions:
        tx_text = f"🔖 {tx['category_name']} | {tx['full_sum']:.2f} ₽ | 📅 {tx['date'][:10]}"
        # ОСТОРОЖНО: description может содержать символы _, лучше не передавать его в callback_data
        # callback_data ограничен 64 байтами. Передавайте только ID.
        # builder.button(text=tx_text, callback_data=f"select_transactionD_{tx['id']}_{tx['description']}") # Ненадежно
        builder.button(text=tx_text, callback_data=f"select_transactionD_{tx['id']}") # Передаем только ID


    builder.button(text="◀ Назад", callback_data=f"transactionD_back_{user_id}")
    builder.adjust(1)
    return builder # <-- Здесь возвращается builder, а не builder.as_markup(). Нужно исправить.

async def choose_buttons_update(user_id, page_transactions):
    builder = InlineKeyboardBuilder()
    for tx in page_transactions:
        tx_text = f"🔖 {tx['category_name']} | {tx['full_sum']:.2f} ₽ | 📅 {tx['date'][:10]}"
        # ОСТОРОЖНО: description может содержать символы _, лучше не передавать его в callback_data
        # callback_data ограничен 64 байтами. Передавайте только ID.
        # builder.button(text=tx_text, callback_data=f"select_transactionU_{tx['id']}_{tx['description']}") # Ненадежно
        builder.button(text=tx_text, callback_data=f"select_transactionU_{tx['id']}") # Передаем только ID


    builder.button(text="◀ Назад", callback_data=f"transactionU_back_{user_id}")
    builder.adjust(1)
    return builder # <-- Здесь возвращается builder, а не builder.as_markup(). Нужно исправить.

async def confirm_or_cancel_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data=f"confirm_delete")
    builder.button(text="❌ Нет", callback_data="cancel_delete")
    builder.adjust(2)
    return builder # <-- Здесь возвращается builder, а не builder.as_markup(). Нужно исправить.

async def back_menu_or_list_transactions():
    builder = InlineKeyboardBuilder()
    builder.button(text='Вернутся к списку ваших записей', callback_data='back_to_list_transactions')
    builder.button(text='Вернутся к меню', callback_data='back_to_menu')
    return builder # <-- Здесь возвращается builder, а не builder.as_markup(). Нужно исправить.

async def retry_or_cancel_keyboard():
    """Клавиатура для повторной попытки или отмены"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Попробовать снова", callback_data="retry_update")
    builder.button(text="❌ Отменить", callback_data="cancel_update")
    return builder # <-- Здесь возвращается builder, а не builder.as_markup(). Нужно исправить.

async def confirm_changes_keyboard():
    """Клавиатура для подтверждения изменений"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="confirm_changes")
    builder.button(text="❌ Отменить", callback_data="cancel_update")
    return builder # <-- Здесь возвращается builder, а не builder.as_markup(). Нужно исправить.

