"""
Модуль для работы с пользователями в базе данных.

Реализует CRUD-операции (Create, Read, Update, Delete) для сущности User
с использованием асинхронного SQLAlchemy.

Основные функции:
- create_user - создание нового пользователя
- get_user - получение пользователя по ID
- get_all_user - получение списка пользователей с пагинацией
- update_user - обновление данных пользователей
- delete_user - удаление пользователя

Особенности реализации:
1. Асинхронная работа с базой данных через AsyncSession
2. Подробное логирование всех операций в JSON-формате
3. Обработка ошибок на уровне БД и бизнес-логики
4. Поддержка частичного обновления через exclude_unset=True
5. Пагинация через параметры skip/limit

Типичный сценарий использования:
```
    from sqlalchemy.ext.asyncio import AsyncSession
    from models import UserCreate
    session = AsyncSession(...)
    data = UserCreate(...)
    user = await create_user(session, data)
```
Логирование:
Все ошибки логируются в формате JSON с полями:
- message - описание операции
- error - текст ошибки
- time - метка времени
- дополнительные параметры операции

Требования:
- SQLAlchemy 2.0+
- Поддержка async/await
- Pydantic для валидации данных
"""
from datetime import datetime
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import DataError, ProgrammingError, NoResultFound, DatabaseError, SQLAlchemyError, InvalidRequestError, DBAPIError, DisconnectionError

from project.db.models.category import User # TODO потом поменять импорт из category
from project.db.schemas.user import UserCreate, UserUpdate

async def create_user(session: AsyncSession, data: UserCreate) -> User | None:
    """
    Создает нового пользователя в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (UserCreate): Данные для создания пользователя.

    Returns:
        User: Созданный объект пользователя или None при ошибке.
    """
    try:
        user = User(**data.model_dump())
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except (ValueError, DataError, ProgrammingError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания пользователя",
            "data": data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_user(session: AsyncSession, user_id: str) -> User | None:
    """
    Получает пользователя по его идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        user_id (int): Идентификатор пользователя.

    Returns:
        User: Объект пользователя, если найден, иначе None.
    """
    if int(user_id) <= 0:
        return None
    try:
        user = await session.execute(select(User).where(User.tg_id == user_id))
        return user.scalar_one_or_none()
    except (NoResultFound, DatabaseError) as e:
        logging.error(json.dumps({
            "message": "Ошибка получения пользователя",
            "user_id": user_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all_users(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Получает список пользователей с диапозоном.

    Пример использования:
        # Получить первые 10 пользователей
        users = await get_all_users(session, skip=0, limit=10)
        
        # Получить следующую порцию (пользователей 11-20)
        next_users = await get_all_users(session, skip=10, limit=10)

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        skip (int): Количество пропускаемых записей (по умолчанию 0).
            Например, skip=10 пропустит первые 10 записей.
        limit (int): Максимальное количество возвращаемых записей (по умолчанию 100).
            Например, limit=20 вернет не более 20 транзакций.

    Returns:
        list[User]: Список пользователей. Возвращает пустой список, если:
            - пользователи отсутствуют
            - указана комбинация skip/limit за пределами общего количества
            - произошла ошибка при запросе
    """
    try:
        users = await session.execute(select(User).offset(skip).limit(limit))
        return users.scalars().all() or []
    except (SQLAlchemyError) as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка пользователей",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
        
async def update_user(session: AsyncSession, user_id: str, data: UserUpdate) -> User | None:
    """
    Обновляет данные пользователя.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        user_id (int): Идентификатор пользователя для обновления.
        data (UserUpdate): Данные для обновления.

    Returns:
        User: Обновленный объект пользователя или None, если пользователь не найден.
    """
    if str(user_id) <= 0:
        return None
    try:
        user = await get_user(session, user_id)
        if not user:
            return None
        
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        
        await session.commit()
        await session.refresh(user)
        return user

    except (InvalidRequestError, AttributeError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка обновления пользователя",
            "data": data.model_dump(),
            "user_id": user_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def delete_user(session: AsyncSession, user_id: str) -> bool:
    """
    Удаляет транзакцию по её идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        user_id (int): Идентификатор пользователя для удаления.

    Returns:
        bool: True, если пользователь удален, False если пользователь не найден.
    """
    if str(user_id) <= 0:
        return False
    try:
        user = await get_user(session, user_id)
        if not user:
            return False
        await session.delete(user)
        await session.commit()
        return True
    except (DBAPIError, DisconnectionError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка удаления пользователя",
            "user_id": user_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return False

# TODO сделать логи через loguru 