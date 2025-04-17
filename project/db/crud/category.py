"""
Модуль для работы с категориями в базе данных.

Реализует CRUD-операции (Create, Read, Update, Delete) для сущности Category
с использованием асинхронного SQLAlchemy.

Основные функции:
- create_category - создание новой категории
- get_category - получение категории по ID
- get_all_categories - получение списка категорий с пагинацией
- update_category - обновление данных категории
- delete_category - удаление категории

Особенности реализации:
1. Асинхронная работа с базой данных через AsyncSession
2. Подробное логирование всех операций в JSON-формате
3. Обработка ошибок на уровне БД и бизнес-логики
4. Поддержка частичного обновления через exclude_unset=True
5. Пагинация через параметры skip/limit

Типичный сценарий использования:
```
    from sqlalchemy.ext.asyncio import AsyncSession
    from models import CategoryCreate
    session = AsyncSession(...)
    data = CategoryCreate(...)
    category = await create_category(session, data)
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

from models.category import Category # TODO потом поменять импорт из category
from schemas.category import CategoryCreate, CategoryUpdate

async def create_category(session: AsyncSession, data: CategoryCreate) -> Category | None:
    """
    Создает новую категорию в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (CategoryCreate): Данные для создания категории.

    Returns:
        Category: Созданный объект категории или None при ошибке.
    """
    try:
        category = Category(**data.model_dump())
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category
    except (ValueError, DataError, ProgrammingError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания категории",
            "data": data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_category(session: AsyncSession, category_id: int) -> Category | None:
    """
    Получает категорию по её идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        category_id (int): Идентификатор категории.

    Returns:
        Category: Объект категории, если найден, иначе None.
    """
    if category_id <= 0:
        return None
    try:
        category = await session.execute(select(Category).where(Category.id == category_id))
        return category.scalar_one_or_none()
    except (NoResultFound, DatabaseError) as e:
        logging.error(json.dumps({
            "message": "Ошибка получения категории",
            "category_id": category_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all_categories(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
    """
    Получает список категорий с диапозоном.

    Пример использования:
        # Получить первые 10 категорий
        categories = await get_all_categories(session, skip=0, limit=10)
        
        # Получить следующую порцию (категорий 11-20)
        next_categ = await get_all_categories(session, skip=10, limit=10)

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        skip (int): Количество пропускаемых записей (по умолчанию 0).
            Например, skip=10 пропустит первые 10 записей.
        limit (int): Максимальное количество возвращаемых записей (по умолчанию 100).
            Например, limit=20 вернет не более 20 транзакций.

    Returns:
        list[Category]: Список категорий. Возвращает пустой список, если:
            - категории отсутствуют
            - указана комбинация skip/limit за пределами общего количества
            - произошла ошибка при запросе
    """
    try:
        categories = await session.execute(select(Category).offset(skip).limit(limit))
        return categories.scalars().all() or []
    except (SQLAlchemyError) as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка категорий",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
        
async def update_category(session: AsyncSession, category_id: int, data: CategoryUpdate) -> Category | None:
    """
    Обновляет данные категории.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        category_id (int): Идентификатор категории для обновления.
        data (CategoryUpdate): Данные для обновления.

    Returns:
        Category: Обновленный объект категории или None, если категория не найдена.
    """
    if category_id <= 0:
        return None
    try:
        category = await get_category(session, category_id)
        if not category:
            return None
        
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(category, key, value)
        
        await session.commit()
        await session.refresh(category)
        return category

    except (InvalidRequestError, AttributeError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка обновления категории",
            "data": data.model_dump(),
            "category_id": category_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def delete_category(session: AsyncSession, category_id: int) -> bool:
    """
    Удаляет категорию по её идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        category_id (int): Идентификатор категории для удаления.

    Returns:
        bool: True, если категория удалена, False если категория не найдена.
    """
    if category_id <= 0:
        return False
    try:
        category = await get_category(session, category_id)
        if not category:
            return False
        await session.delete(category)
        await session.commit()
        return True
    except (DBAPIError, DisconnectionError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка удаления категории",
            "category_id": category_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return False

# TODO сделать логи через loguru 