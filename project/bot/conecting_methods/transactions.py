import logging
import httpx
from project.core.request_conf import *

async def create_transaction(params:dict, data: dict):
    """
    Создает новую транзакцию на сервере.

    Пример использования:
        data = {"amount": 1000, "category": "Зарплата", "type": 1, "user_id": 1}
        result = await create_transaction(data)

    Args:
        data (dict): Данные транзакции для отправки на сервер.

    Returns:
        dict: Ответ от сервера с деталями созданной транзакции.

    Raises:
        HTTPStatusError: Если запрос завершился с ошибкой (например, 400 или 500).
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{URL}{TRANSACTIONS}',params=params, json=data)
            response.raise_for_status()
            if response.status_code == 200:
                result = response.json()
                return result
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при создании транзакции: {str(e)}")
        raise httpx.HTTPStatusError(message="Произошла ошибка при создании транзакции")

async def get_transaction(transaction_id: int):
    """
    Получает данные транзакции по её ID.

    Пример использования:
        transaction = await get_transaction(5)

    Args:
        transaction_id (int): Идентификатор нужной транзакции.

    Returns:
        dict: Информация о транзакции, если она найдена.

    Raises:
        HTTPStatusError: Если транзакция не найдена или произошла ошибка запроса.
    """
 
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{TRANSACTIONS}{transaction_id}')
            response.raise_for_status()
            if response.status_code == 200:
                result = response.json()
                return result
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при получении транзакции: {str(e)}")
        raise httpx.HTTPStatusError(message="Произошла ошибка при получении транзакции")

async def get_transactions(user_id: int):
    """
    Получает все транзакции пользователя.

    Пример использования:
        transactions = await get_transactions(user_id=1)

    Args:
        user_id (int): Идентификатор пользователя, чьи транзакции нужно получить.

    Returns:
        dict: Список транзакций, сгруппированных по дате или категории.

    Raises:
        HTTPStatusError: В случае ошибки при получении данных.
    """

    try:
        async with httpx.AsyncClient() as client:
            params = {'user_id': user_id}
            response = await client.get(f'{URL}{TRANSACTIONS}', params=params)
            response.raise_for_status()
            if response.status_code == 200:
                result = response.json()
                return result
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при получении транзакции: {str(e)}")
        raise httpx.HTTPStatusError(message="Произошла ошибка при получении транзакции")    

async def update_transaction(user_id:int,transaction_id: int, update_data: dict):
    """
    Обновляет данные транзакции по её ID.

    Пример использования:
        updated = await update_transaction(3, {"amount": 2000})

    Args:
        transaction_id (int): Идентификатор обновляемой транзакции.
        update_data (dict): Словарь с изменениями.

    Returns:
        dict: Обновлённые данные транзакции.

    Raises:
        HTTPStatusError: Если обновление не удалось или произошла ошибка.
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(f'{URL}{TRANSACTIONS}{transaction_id}', params={'user_id': user_id},json=update_data)
            response.raise_for_status()
            if response.status_code == 200:
                result = response.json()
                return result
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при обновлении транзакции: {str(e)}")
        raise httpx.HTTPStatusError(message="Произошла ошибка при обновлении транзакции")

async def delete_transaction(transaction_id: int):
    """
    Удаляет транзакцию по её ID.

    Пример использования:
        result = await delete_transaction(7)

    Args:
        transaction_id (int): Идентификатор удаляемой транзакции.

    Returns:
        dict: Ответ сервера о результате удаления.

    Raises:
        HTTPStatusError: Если транзакция не существует или возникла ошибка при удалении.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f'{URL}{TRANSACTIONS}{transaction_id}')
            response.raise_for_status()
            if response.status_code == 200:
                result = response.json()
                return result
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при удалении транзакции: {str(e)}")
        raise httpx.HTTPStatusError(message="Произошла ошибка при удалении транзакции")

async def get_statistics_from_month(month: int, user_id: int):
    """
    Получает статистику за указанный месяц для пользователя.

    Пример использования:
        stats = await get_statistics_from_month(4, user_id=1)

    Args:
        month (int): Номер месяца (1–12), за который нужна статистика.
        user_id (int): Идентификатор пользователя.

    Returns:
        dict: Сводка статистики за месяц (доходы, расходы, топ категории).

    Raises:
        HTTPStatusError: Если данные не удалось получить.
    """
    try:
        async with httpx.AsyncClient() as client:
            params = {
                'user_id': user_id
            }
            response = await client.get(f'{URL}{TRANSACTIONS}{FROM_MONTH}{month}', params=params)
            response.raise_for_status()
            if response.status_code == 200:
                result = response.json() 
                return result
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при получении статистики за месяц: {str(e)}")
        raise httpx.HTTPStatusError(message="Произошла ошибка при получении статистики за месяц")

async def get_statistics_from_period(data: dict):
    """
    Получает статистику за произвольный период времени.

    Пример использования:
        data = {"user_id": 1, "from_date": "2025-04-01", "to_date": "2025-04-30"}
        stats = await get_statistics_from_period(data)

    Args:
        data (dict): Параметры запроса, включая user_id, from_date и to_date.

    Returns:
        dict: Статистика за указанный период.

    Raises:
        HTTPStatusError: В случае ошибки запроса.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{TRANSACTIONS}{STATISTICS}', params=data)
            response.raise_for_status()
            if response.status_code == 200:
                result = response.json() 
                return result
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при получении статистики за период: {str(e)}")
        raise httpx.HTTPStatusError(message="Произошла ошибка при получении статистики за период")