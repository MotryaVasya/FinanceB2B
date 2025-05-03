import logging
import httpx
from project.core.request_conf import *

async def create_transaction(data: dict):
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
            response = await client.post(f'{URL}{TRANSACTIONS}', json=data)
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

async def update_transaction(transaction_id: int, update_data: dict, user_id: int): # Добавляем user_id
    """
    Обновляет данные транзакции по её ID.
    ...
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f'{URL}{TRANSACTIONS}{transaction_id}',
                params={'user_id': user_id}, # Добавляем user_id как query parameter
                json=update_data
            )
            response.raise_for_status()
            if response.status_code == 200:
                return response.json()
    except httpx.HTTPStatusError as e:
        logging.error(f"Ошибка HTTP при обновлении транзакции ID {transaction_id}: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
                logging.error(f"Тело ответа при ошибке {e.response.status_code}: {error_detail}") # Логируем детали ошибки
            except Exception:
                logging.error(f"Тело ответа (не JSON) при ошибке {e.response.status_code}: {e.response.text}")
        raise e # Перевыбрасываем пойманное исключение
    except Exception as e:
         logging.error(f"Неожиданная ошибка при обновлении транзакции ID {transaction_id}: {e}")
         raise e

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

async def get_transactions(user_id: int, page: int = 1, per_page: int = 10) -> list:
    """
    Получает транзакции пользователя с пагинацией.

    Args:
        user_id (int): ID пользователя
        page (int): Номер страницы
        per_page (int): Количество записей на странице

    Returns:
        list: Список транзакций или пустой список при ошибке
    """
    try:
        async with httpx.AsyncClient() as client:
            params = {
                'user_id': user_id,
                'page': page,
                'per_page': per_page
            }
            response = await client.get(
                f'{URL}{TRANSACTIONS}',
                params=params,
                timeout=10.0
            )

            if response.status_code == 200:
                return response.json() or []
            elif response.status_code == 404:
                return []
            else:
                response.raise_for_status()
                return []

    except httpx.HTTPStatusError as e:
        logging.error(f"Ошибка HTTP при получении транзакций: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Неожиданная ошибка при получении транзакций: {str(e)}")
        return []
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