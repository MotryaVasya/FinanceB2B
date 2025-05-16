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

from project.db.models.category import Category, User # TODO потом поменять импорт из category
from project.db.schemas.category import CategoryCreate, CategoryUpdate

async def create_category(user_id: int, session: AsyncSession, data: CategoryCreate) -> Category | None:
    """
    Создает новую категорию в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (CategoryCreate): Данные для создания категории.

    Returns:
        Category: Созданный объект категории или None при ошибке.
    """
    try:
        user_id_subquery = select(User.id).where(User.tg_id == user_id).scalar_subquery()
        category = Category(
            name_category=data.name_category,
            type=data.type,
            user_id=user_id_subquery
        )
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category.to_pydantic()
    except (ValueError, DataError, ProgrammingError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания категории",
            "data": data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_category(session: AsyncSession, category_id: int, as_pydantic: bool = True) -> Category | None:
    """
    Получает категорию по её идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        category_id (int): Идентификатор категории.
        as_pydantic (bool): Переводит в тип (pydantic) если True, иначе тип Category

    Returns:
        Category: Объект категории, если найден, иначе None.
    """
    if category_id <= 0:
        return None
    try:
        result = await session.execute(select(Category).filter(Category.id == category_id))
        if not result:
            return None
        category = result.scalars().first()
        if as_pydantic:
            return category.to_pydantic() if category else None
        else:
            return category if category else None
    except (NoResultFound, DatabaseError) as e:
        logging.error(json.dumps({
            "message": "Ошибка получения категории",
            "category_id": category_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all_categories(user_id: int, session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
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
        user_id_subquery = select(User.id).where(User.tg_id == user_id).scalar_subquery()

        result = await session.execute(select(Category)
                                       .where((Category.user_id == user_id_subquery) | 
                                              (Category.user_id == None))
                                       .order_by(Category.user_id.desc())
                                       .offset(skip)
                                       .limit(limit))
        categories = result.scalars().all()
        return [category.to_pydantic() for category in categories] or []
    except (SQLAlchemyError) as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка категорий",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
        

async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
    """
    Получает список категорий с диапозоном.

    Пример использования:
        # Получить первые 10 категорий
        categories = await get_all(session, skip=0, limit=10)
        
        # Получить следующую порцию (категорий 11-20)
        next_categ = await get_all(session, skip=10, limit=10)

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
        result = await session.execute(select(Category)
                                       .offset(skip)
                                       .limit(limit))
        categories = result.scalars().all()
        return [category.to_pydantic() for category in categories] or []
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
        category = await get_category(session, category_id, False)
        if not category:
            return None
        
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(category, key, value)
        
        await session.commit()
        await session.refresh(category)
        return category.to_pydantic()

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
        category = await get_category(session, category_id, False)
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