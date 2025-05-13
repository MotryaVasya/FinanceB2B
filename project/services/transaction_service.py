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

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from project.db.crud import transaction as crud
from project.db.schemas.transaction import TransactionCreate, TransactionStatistics, TransactionUpdate
from project.db.models.category import Transaction # TODO потом поменять импорт из category

async def create(user_id: str, session: AsyncSession, data: TransactionCreate)-> Transaction | None:
    """Создает новую транзакцию.

    Args:
        session: Асинхронная сессия БД
        data: Валидированные данные для создания транзакции
        
    Returns:
        Созданный объект транзакции или None при ошибке
    """
    return await crud.create_transaction(user_id, session, data)

async def get(session: AsyncSession, transaction_id: int) -> Transaction | None:
    """Получает транзакцию по идентификатору.
    
    Args:
        session: Асинхронная сессия БД
        transaction_id: Уникальный ID транзакции
        
    Returns:
        Объект транзакции или None если не найдена
    """
    return await crud.get_transaction(session, transaction_id)

async def get_all(user_id: str, session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Transaction]:
    """Получает список транзакций с пагинацией.
    
    Args:
        session: Асинхронная сессия БД
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        
    Returns:
        Список транзакций (может быть пустым)
    """
    return await crud.get_all_transactions(user_id, session, skip, limit)

async def update(user_id: str, session: AsyncSession, transaction_id: int, data: TransactionUpdate) -> Transaction | None:
    """Обновляет данные транзакции.
    
    Args:
        session: Асинхронная сессия БД
        transaction_id: Уникальный ID транзакции
        data: Данные для частичного обновления
        
    Returns:
        Обновленный объект транзакции или None если транзакция не найдена
    """
    return await crud.update_transaction(user_id, session, transaction_id, data)

async def delete(session: AsyncSession, transaction_id: int) -> bool:
    """Удаляет транзакцию.
    
    Args:
        session: Асинхронная сессия БД
        transaction_id: Уникальный ID транзакции
        
    Returns:
        True если удаление успешно, False если транзакция не найдена
    """
    return await crud.delete_transaction(session, transaction_id)

async def get_from_month(session: AsyncSession, month: int, user_id: str) -> list[Transaction]:
    """Получает список транзакций за указанный диапазон дат.

    Args:
        session: Асинхронная сессия БД.
        from_date: Начальная дата диапазона.
        to_date: Конечная дата диапазона.

    Returns:
        Список транзакций, у которых дата попадает в указанный диапазон (включительно).
    """
    return await crud.get_transactions_from_month(session, month, user_id)

async def get_statistics(session: AsyncSession, from_date: datetime, to_date: datetime, user_id: str) -> TransactionStatistics:
    """
    Получает топ-3 категории по количеству транзакций для указанного пользователя в указанный период времени.

    Эта функция вызывает функцию из модуля `crud`, чтобы извлечь данные по категориям, отсортированные по количеству транзакций
    для конкретного пользователя (`user_id`) в пределах указанного диапазона дат (`from_date`, `to_date`).

    Args:
        session (AsyncSession): Асинхронная сессия БД, предоставляемая для работы с данными.
        from_date (datetime): Начальная дата периода, за который нужно получить данные.
        to_date (datetime): Конечная дата периода, за который нужно получить данные.
        user_id (int): Идентификатор пользователя, для которого нужно получить топ-3 категории.

    Returns:
        list: Список категорий с их именами и количеством транзакций для указанного пользователя в периоде.
            Если произошла ошибка, будет возвращен пустой список.
    """
    return await crud.get_statistics(session, from_date, to_date, user_id)
    