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
