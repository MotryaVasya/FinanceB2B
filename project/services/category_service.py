"""
Модуль бизнес-логики для работы с категориями.

Служит промежуточным слоем между API-роутерами и CRUD-операциями,
предоставляя чистый интерфейс для работы с категориями.

Архитектурные особенности:
- Асинхронный интерфейс
- Типизированные параметры и возвращаемые значения
- Делегирование низкоуровневых операций CRUD-слою
- Поддержка пагинации для списковых запросов
"""
from sqlalchemy.ext.asyncio import AsyncSession
from project.db.crud import category as crud
from project.db.schemas.category import CategoryCreate, CategoryUpdate
from project.db.models.category import Category # TODO потом поменять импорт из category

async def create(session: AsyncSession, data: CategoryCreate)-> Category | None:
    """Создает новую категорию.

    Args:
        session: Асинхронная сессия БД
        data: Валидированные данные для создания категории
        
    Returns:
        Созданный объект категории или None при ошибке
    """
    return await crud.create_category(session, data)

async def get(session: AsyncSession, category_id: int) -> Category | None:
    """Получает категорию по идентификатору.
    
    Args:
        session: Асинхронная сессия БД
        category_id: Уникальный ID категории
        
    Returns:
        Объект категории или None если не найден
    """
    return await crud.get_category(session, category_id)

async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
    """Получает список категорий с пагинацией.
    
    Args:
        session: Асинхронная сессия БД
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        
    Returns:
        Список категорий (может быть пустым)
    """
    return await crud.get_all_categories(session, skip, limit)

async def update(session: AsyncSession, category_id: int, data: CategoryUpdate) -> Category | None:
    """Обновляет данные категории.
    
    Args:
        session: Асинхронная сессия БД
        category_id: Уникальный ID категории
        data: Данные для частичного обновления
        
    Returns:
        Обновленный объект категории или None если категория не найдена
    """
    return await crud.update_category(session, category_id, data)

async def delete(session: AsyncSession, category_id: int) -> bool:
    """Удаляет категорию.
    
    Args:
        session: Асинхронная сессия БД
        category_id: Уникальный ID категории
        
    Returns:
        True если удаление успешно, False если категория не найдена
    """
    return await crud.delete_category(session, category_id)