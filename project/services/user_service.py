"""
Модуль бизнес-логики для работы с пользователями.

Служит промежуточным слоем между API-роутерами и CRUD-операциями,
предоставляя чистый интерфейс для работы с пользователями.

Архитектурные особенности:
- Асинхронный интерфейс
- Типизированные параметры и возвращаемые значения
- Делегирование низкоуровневых операций CRUD-слою
- Поддержка пагинации для списковых запросов
"""
from sqlalchemy.ext.asyncio import AsyncSession
from db.crud import user as crud
from db.schemas.user import UserCreate, UserUpdate
from db.models.category import User # TODO потом поменять импорт из category

async def create(session: AsyncSession, data: UserCreate)-> User | None:
    """Создает нового пользователя.

    Args:
        session: Асинхронная сессия БД
        data: Валидированные данные для создания пользователя
        
    Returns:
        Созданный объект пользователя или None при ошибке
    """
    return await crud.create_user(session, data)

async def get(session: AsyncSession, user_id: int) -> User | None:
    """Получает пользователя по идентификатору.
    
    Args:
        session: Асинхронная сессия БД
        user_id: Уникальный ID пользователя
        
    Returns:
        Объект пользователя или None если не найден
    """
    return await crud.get_user(session, user_id)

async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """Получает список пользователей с пагинацией.
    
    Args:
        session: Асинхронная сессия БД
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        
    Returns:
        Список пользователей (может быть пустым)
    """
    return await crud.get_all_users(session, skip, limit)

async def update(session: AsyncSession, user_id: int, data: UserUpdate) -> User | None:
    """Обновляет данные пользователя.
    
    Args:
        session: Асинхронная сессия БД
        user_id: Уникальный ID пользователя
        data: Данные для частичного обновления
        
    Returns:
        Обновленный объект пользователя или None если пользователь не найден
    """
    return await crud.update_user(session, user_id, data)

async def delete(session: AsyncSession, user_id: int) -> bool:
    """Удаляет пользователя.
    
    Args:
        session: Асинхронная сессия БД
        user_id: Уникальный ID пользователя
        
    Returns:
        True если удаление успешно, False если пользователь не найден
    """
    return await crud.delete_user(session, user_id)