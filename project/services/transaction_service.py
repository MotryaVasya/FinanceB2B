"""
Модуль бизнес-логики для работы с транзакциями.

Служит промежуточным слоем между API-роутерами и CRUD-операциями,
предоставляя чистый интерфейс для работы с транзакциями.

Архитектурные особенности:
- Асинхронный интерфейс
- Типизированные параметры и возвращаемые значения
- Делегирование низкоуровневых операций CRUD-слою
- Поддержка пагинации для списковых запросов
"""

from sqlalchemy.ext.asyncio import AsyncSession
from db.crud import transaction as crud
from db.schemas.transaction import TransactionCreate, TransactionUpdate
from db.models.category import Transaction # TODO потом поменять импорт из category

async def create(session: AsyncSession, data: TransactionCreate)-> Transaction | None:
    """Создает новую транзакцию.

    Args:
        session: Асинхронная сессия БД
        data: Валидированные данные для создания транзакции
        
    Returns:
        Созданный объект транзакции или None при ошибке
    """
    return await crud.create_transaction(session, data)

async def get(session: AsyncSession, transaction_id: int) -> Transaction | None:
    """Получает транзакцию по идентификатору.
    
    Args:
        session: Асинхронная сессия БД
        transaction_id: Уникальный ID транзакции
        
    Returns:
        Объект транзакции или None если не найдена
    """
    return await crud.get_transaction(session, transaction_id)

async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Transaction]:
    """Получает список транзакций с пагинацией.
    
    Args:
        session: Асинхронная сессия БД
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        
    Returns:
        Список транзакций (может быть пустым)
    """
    return await crud.get_all_transactions(session, skip, limit)

async def update(session: AsyncSession, transaction_id: int, data: TransactionUpdate) -> Transaction | None:
    """Обновляет данные транзакции.
    
    Args:
        session: Асинхронная сессия БД
        transaction_id: Уникальный ID транзакции
        data: Данные для частичного обновления
        
    Returns:
        Обновленный объект транзакции или None если транзакция не найдена
    """
    return await crud.update_transaction(session, transaction_id, data)

async def delete(session: AsyncSession, transaction_id: int) -> bool:
    """Удаляет транзакцию.
    
    Args:
        session: Асинхронная сессия БД
        transaction_id: Уникальный ID транзакции
        
    Returns:
        True если удаление успешно, False если транзакция не найдена
    """
    return await crud.delete_transaction(session, transaction_id)