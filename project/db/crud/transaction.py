"""
Модуль для работы с транзакциями в базе данных.

Реализует CRUD-операции (Create, Read, Update, Delete) для сущности Transaction
с использованием асинхронного SQLAlchemy.

Основные функции:
- create_transaction - создание новой транзакции
- get_transaction - получение транзакции по ID
- get_all_transactions - получение списка транзакций с пагинацией
- update_transaction - обновление данных транзакции
- delete_transaction - удаление транзакции

Особенности реализации:
1. Асинхронная работа с базой данных через AsyncSession
2. Подробное логирование всех операций в JSON-формате
3. Обработка ошибок на уровне БД и бизнес-логики
4. Поддержка частичного обновления через exclude_unset=True
5. Пагинация через параметры skip/limit

Типичный сценарий использования:
```
    from sqlalchemy.ext.asyncio import AsyncSession
    from models import TransactionCreate
    session = AsyncSession(...)
    data = TransactionCreate(...)
    transaction = await create_transaction(session, data)
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

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import DataError, ProgrammingError, NoResultFound, DatabaseError, SQLAlchemyError, InvalidRequestError, DBAPIError, DisconnectionError

from project.db.models.category import Transaction # TODO потом поменять импорт из category
from project.db.schemas.transaction import TransactionCreate, TransactionUpdate

async def parse_naive_datetime(date_input: str | datetime) -> datetime:
    """
    Преобразует строку или datetime в naive datetime (без таймзоны).
    Бросает HTTPException при ошибке парсинга или наличии tzinfo.
    """
    if isinstance(date_input, str):
        try:
            date_input = datetime.fromisoformat(date_input)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Неверный формат даты. Используй ISO 8601, например: '2025-04-23T14:30:00'"
            )
    if date_input.tzinfo is not None:
        date_input = date_input.replace(tzinfo=None)
    return date_input


async def create_transaction(session: AsyncSession, data: TransactionCreate) -> Transaction | None:
    """
    Создает новую транзакцию в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (TransactionCreate): Данные для создания транзакции.

    Returns:
        Transaction: Созданный объект транзакции или None при ошибке.
    """
    try:
        parsed_date = await parse_naive_datetime(data.date)

        transaction = Transaction(
            description=data.description,
            full_sum=data.full_sum,
            date=parsed_date,
            category_id=data.category_id,
            user_id=data.user_id
        )

        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)

        result = transaction.to_pydantic()
        if result is None:
            raise ValueError("Failed to convert transaction to Pydantic model")
            
        return result
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используй ISO формат: YYYY-MM-DDTHH:MM:SS")

    except (DataError, ProgrammingError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания транзакции",
            "data": data.model_dump(),
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_transaction(session: AsyncSession, transaction_id: int, as_pydantic: bool = True) -> Transaction | None:
    """
    Получает транзакцию по её идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        transaction_id (int): Идентификатор транзакции.
        as_pydantic (bool): Переводит в тип (pydantic) если True, иначе тип Transaction
    Returns:
        Transaction: Объект транзакции, если найден, иначе None.
    """
    if transaction_id <= 0:
        return None
    try:
        result = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction = result.scalars().first()
        if transaction is None:
            return None
        if as_pydantic:
            return transaction.to_pydantic()
        else:
            return transaction
    except (NoResultFound, DatabaseError) as e:
        logging.error(json.dumps({
            "message": "Ошибка получения транзакции",
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all_transactions(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Transaction]:
    """
    Получает список транзакций с диапозоном.

    Пример использования:
        # Получить первые 10 транзакций
        transactions = await get_all_transactions(session, skip=0, limit=10)
        
        # Получить следующую порцию (транзакции 11-20)
        next_transact = await get_all_transactions(session, skip=10, limit=10)

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        skip (int): Количество пропускаемых записей (по умолчанию 0).
            Например, skip=10 пропустит первые 10 записей.
        limit (int): Максимальное количество возвращаемых записей (по умолчанию 100).
            Например, limit=20 вернет не более 20 транзакций.

    Returns:
        list[Transaction]: Список транзакций. Возвращает пустой список, если:
            - транзакции отсутствуют
            - указана комбинация skip/limit за пределами общего количества
            - произошла ошибка при запросе
    """
    try:
        result = await session.execute(select(Transaction).offset(skip).limit(limit))
        transactions = result.scalars().all()
        return [transaction.to_pydantic() for transaction in transactions] or []
    except (SQLAlchemyError) as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка транзакций",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
        
async def update_transaction(session: AsyncSession, transaction_id: int, data: TransactionUpdate) -> Transaction | None:
    if transaction_id <= 0:
        return None
    try:
        transaction = await get_transaction(session, transaction_id, as_pydantic=False)
        if not transaction:
            return None

        updates = data.model_dump(exclude_unset=True)

        if "date" in updates:
           updates['date'] = await parse_naive_datetime(updates["date"])

        for key, value in updates.items():
            setattr(transaction, key, value)

        await session.commit()
        await session.refresh(transaction)
        return transaction.to_pydantic()

    except (InvalidRequestError, AttributeError, TypeError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка обновления транзакции",
            "data": data.model_dump(),
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении транзакции"
        )


async def delete_transaction(session: AsyncSession, transaction_id: int) -> bool:
    """
    Удаляет транзакцию по её идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        transaction_id (int): Идентификатор транзакции для удаления.

    Returns:
        bool: True, если транзакция удалена, False если транзакция не найдена.
    """
    if transaction_id <= 0:
        return False
    try:
        transaction = await get_transaction(session, transaction_id, False)
        if not transaction:
            return False
        await session.delete(transaction)
        await session.commit()
        return True
    except (DBAPIError, DisconnectionError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка удаления транзакции",
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return False

