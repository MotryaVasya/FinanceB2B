PAGE_SIZE = 3  # Количество транзакций на странице
user_pages = {} # Словарь для хранения текущей страницы пользователя {user_id: page}

async def get_paginated_transactions(user_id: int, page: int = 0):
    from project.bot.conecting_methods.transactions import get_transactions
    all_transactions = await get_transactions(user_id)
    total_pages = (len(all_transactions) + PAGE_SIZE - 1) // PAGE_SIZE
    
    # Получаем транзакции для текущей страницы
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_transactions = all_transactions[start_idx:end_idx]
    
    # Форматируем сообщение
    formatted = []
    for tx in page_transactions: # TODO надо будет поменять текст 
        date = tx['date'][:10]
        formatted.append(
            f"🔖 {tx['category_name']}\n"
            f"📅 {date} | {tx['full_sum']:.2f} ₽\n"
            f"📝 {tx['description'] or 'Нет описания'}\n"
            f"━━━━━━━━━━━━━━━━━"
        )
    message = "\n\n".join(formatted)
    message += f"\n\nСтраница {page + 1}/{total_pages}"
    
    return message, total_pages

async def get_paginated_category(user_id: int, page: int = 0, for_show: bool = False):
    from project.bot.conecting_methods.category import get_categories
    all_categories = await get_categories(user_id)
    
    if for_show:
        # Для показа сортируем все категории: сначала пользовательские, потом общие
        all_categories_sorted = sorted(
            all_categories,
            key=lambda x: (0 if x['user_id'] else 1, x['name_category'])  # Исправлено на name_category
        )
    else:
        # Для операций обновления/удаления берем только пользовательские категории
        all_categories_sorted = sorted(
            [cat for cat in all_categories if cat['user_id']],
            key=lambda x: x['name_category']  # Исправлено на name_category
        )
    
    total_pages = max(1, (len(all_categories_sorted) + PAGE_SIZE - 1) // PAGE_SIZE)
    
    # Получаем категории для текущей страницы
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_categories = all_categories_sorted[start_idx:end_idx]
    
    # Форматируем сообщение
    formatted = []
    for tx in page_categories:
        # Определяем тип категории
        category_type = 'Доход' if tx['type'] == 1 else 'Расход'
        
        formatted.append(
            f"🔖 {tx['name_category']}\n"  # Исправлено на name_category
            f"📝 Тип: {category_type}\n"
            f"━━━━━━━━━━━━━━━━━"
        )
    
    # Формируем итоговое сообщение
    header = "Ваши категории:\n\n" if for_show else "Список категорий для изменения:\n\n"
    message = header + "\n\n".join(formatted)
    message += f"\n\nСтраница {page + 1}/{total_pages}"
    
    return message, total_pages