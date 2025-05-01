import logging
import httpx
from project.core.request_conf import *

async def create_user(data: dict):
    """
    Создает нового пользователя на сервере.

    Пример использования:
        new_user = await create_user({"name": "Иван", "email": "ivan@example.com"})

    Args:
        data (dict): Данные нового пользователя (например, имя, email и т.д.).

    Returns:
        dict: Информация о созданном пользователе.

    Raises:
        HTTPStatusError: Если при создании пользователя произошла ошибка (например, пользователь уже существует).
    """
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f'{URL}{USERS}{data['tg_id']}')
            if res.status_code == 404:
                response = await client.post(f'{URL}{USERS}', json=data)
                response.raise_for_status()
                if response.status_code == 200:
                    result = response.json()
                    return result
            return
    except httpx._exceptions.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при создании пользователя: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при создании пользователя")

async def get_user(user_id: int):
    """
    Асинхронно отправляет GET-запрос для получения данных пользователя по его ID.
    
    Параметры:
        user_id (int): Уникальный идентификатор пользователя.

    Возвращает:
        dict: Ответ от сервера с данными пользователя, если запрос успешен.

    Исключения:
        HTTPStatusError: В случае ошибки HTTP (например, если пользователь не найден).
    """ 
    try:
        async with httpx.AsyncClient() as client:

            response = await client.get(f'{URL}{USERS}{user_id}')
            response.raise_for_status()
            if response.status_code == 200:
                data = response.json()
                return data
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при получения данных пользователя: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получения данных пользователя")