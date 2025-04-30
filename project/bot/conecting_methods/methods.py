from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from project.bot.keyboards.inline_transactions import build_pagination_keyboard_for_delete, build_pagination_keyboard_for_update, choose_buttons_delete, choose_buttons_update

from project.bot.messages.mesage_transaction import PAGE_SIZE, get_paginated_transactions


async def check_action(action: str, 
                     total_pages: int, 
                     current_page: int, 
                     callback: CallbackQuery, 
                     state: FSMContext = None, 
                     for_update: bool = False, 
                     for_delete: bool = False, 
                     all_transactions = None, 
                     user_id = None):
    """Обрабатывает действия пагинации и выбор элементов для операций update/delete.
    
    Функция является центральным роутером действий для:
    - Навигации по страницам (вперед/назад, прыжки по 5 страниц)
    - Выбора конкретных транзакций для операций
    - Возврата к списку после выбора

    Args:
        action (str): Тип действия из callback_data:
            - 'prev', 'next' - постраничная навигация
            - 'back5', 'forward5' - переход на 5 страниц
            - 'first', 'last' - крайние страницы
            - 'choose' - выбор элемента
            - 'back' - возврат к списку
        total_pages (int): Общее количество страниц
        current_page (int): Текущая страница (0-based)
        callback (CallbackQuery): Объект callback от Telegram
        state (FSMContext, optional): Контекст состояния для сохранения данных
        for_update (bool): Флаг режима обновления транзакций
        for_delete (bool): Флаг режима удаления транзакций
        all_transactions (list, optional): Полный список транзакций
        user_id (int, optional): ID пользователя для персонализации

    Returns:
        int|None: 
            - Новый номер страницы (для навигации)
            - None (при операциях выбора/возврата)

    Raises:
        Exception: Логирует ошибки в консоль, но не прерывает работу

    Examples:
        >>> # Навигация
        >>> await check_action('next', 5, 2, callback)
        3
        
        >>> # Выбор для удаления
        >>> await check_action('choose', 5, 2, callback, state, for_delete=True)
        None
    """
    try:
        if for_delete:
            if action == "choose":
                if not all_transactions:
                    await callback.answer("Нет транзакций для выбора")
                    return current_page
                
                start_idx = current_page * PAGE_SIZE
                page_transactions = all_transactions[start_idx:start_idx + PAGE_SIZE]
                
                builder = await choose_buttons_delete(user_id, page_transactions)
                await state.update_data(original_message=callback.message.text)
                
                await callback.message.edit_text(
                    text=f"{callback.message.text}\n\nВыберите транзакцию для удаления:",
                    reply_markup=builder.as_markup()
                )
                return None
                
            elif action == "back":
                data = await state.get_data()
                original_message = data.get('original_message', "Список транзакций")
                keyboard = await build_pagination_keyboard_for_delete(current_page, total_pages, user_id)
                await callback.message.edit_text(text=original_message, reply_markup=keyboard)
                return None
            
        elif for_update:
            if action == "choose":
                await state.update_data(original_message=callback.message.text)
                
                # Получаем транзакции текущей страницы
                start_idx = current_page * PAGE_SIZE
                page_transactions = all_transactions[start_idx:start_idx + PAGE_SIZE]
                
                builder = await choose_buttons_update(user_id, page_transactions)
                
                await callback.message.edit_text(
                    text=callback.message.text + "\n\nВыберите транзакцию для обновления:",
                    reply_markup=builder.as_markup()
                )
                await callback.answer()
                return
            
            elif action == "back":
                # Восстанавливаем исходное сообщение из состояния
                data = await state.get_data()
                original_message = data.get('original_message', "Список транзакций")
                
                message_text, total_pages = await get_paginated_transactions(user_id, current_page)
                keyboard = await build_pagination_keyboard_for_update(current_page, total_pages, user_id)
                
                await callback.message.edit_text(
                    text=original_message,
                    reply_markup=keyboard
                )
                await callback.answer()
                return
                
        # Обработка обычных действий пагинации
        if action == "prev":
            return max(0, current_page - 1)
        elif action == "next":
            return min(total_pages - 1, current_page + 1)
        elif action == "back5":
            return max(0, current_page - 5)
        elif action == "forward5":
            return min(total_pages - 1, current_page + 5)
        elif action == "first":
            return 0
        elif action == "last":
            return total_pages - 1
        
        await callback.answer("Неизвестное действие")
        return current_page
        
    except Exception as e:
        print(f"Ошибка в check_action: {e}")
        await callback.answer("Ошибка обработки действия")
        return current_page