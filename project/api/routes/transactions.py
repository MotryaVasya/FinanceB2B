from datetime import datetime
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from project.db.schemas.transaction import TransactionCreate, TransactionStatistics, TransactionUpdate, TransactionOut
from project.db.session import get_db 
from project.services import transaction_service

router = APIRouter(prefix='/transactions', tags=['Transactions'])

@router.post('/', response_model=TransactionOut)
async def create_transaction(data: TransactionCreate, db: AsyncSession = Depends(get_db)):
    """
    Создаёт новую транзакцию в базе данных.

    Args:
        data (TransactionCreate): Данные для создания транзакции.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        TransactionOut: Возвращает созданную транзакцию.
    """
    try:
        return await transaction_service.create(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при создании транзакции на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/', response_model=list[TransactionOut])
async def get_transactions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Получает список всех транзакций с поддержкой пагинации.

    Args:
        skip (int): Количество пропущенных транзакций (по умолчанию 0).
        limit (int): Количество транзакций для возврата (по умолчанию 100).
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        list[TransactionOut]: Список транзакций.
    """
    try:
        return await transaction_service.get_all(db, skip, limit)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении транзакций на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get("/get_statistics", response_model=TransactionStatistics)
async def get_top_categories_by_user(from_date: datetime, to_date: datetime, user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает статистику по транзакциям пользователя за указанный период:
    доходы, расходы и топ-3 категории.

    Args:
        from_date (datetime): Начальная дата диапазона.
        to_date (datetime): Конечная дата диапазона.
        user_id (int): ID пользователя.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        TransactionStatistics: Статистика по транзакциям пользователя.
    """
    try:
        return await transaction_service.get_statistics(db, from_date, to_date, user_id)
    except Exception as e:
        logging.error(f"Ошибка получения топ-3 категорий для пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")

@router.get('/{transaction_id}', response_model=TransactionOut, 
            responses={404: {
                "description": "Transaction not found",}})
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает транзакцию по её ID.

    Args:
        transaction_id (int): ID транзакции.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        TransactionOut: Транзакция с указанным ID.
        HTTPException: Если транзакция не найдена.
    """
    try:
        transaction = await transaction_service.get(db, transaction_id)
        if transaction is None:
            raise HTTPException(404, 'Transaction not found')
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении транзакции на стороне API",
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/from_month/{month}', response_model=TransactionStatistics)
async def get_transactions(month: int, user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает статистику транзакций пользователя за указанный месяц.

    Args:
        month (int): Номер месяца (от 1 до 12).
        user_id (int): ID пользователя.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        TransactionStatistics: Статистика по транзакциям за месяц.
    """
    try:
        return await transaction_service.get_from_month(db, month, user_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении транзакций за месяц на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.put('/{transaction_id}', response_model=TransactionOut)
async def update_transaction(transaction_id: int, data: TransactionUpdate, db: AsyncSession = Depends(get_db)):
    """
    Обновляет информацию о транзакции по её ID.

    Args:
        transaction_id (int): ID транзакции, которую нужно обновить.
        data (TransactionUpdate): Данные для обновления транзакции.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        TransactionOut: Обновленная транзакция.
        HTTPException: Если транзакция не найдена.
    """
    try:
        transaction = await transaction_service.update(db, transaction_id, data)
        if transaction is None:
            raise HTTPException(404, "Transaction not found")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при обновлении транзакции на стороне API",
            "data": data,
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.delete('/{transaction_id}')
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаляет транзакцию по её ID.

    Args:
        transaction_id (int): ID транзакции, которую нужно удалить.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        HTTPException: Если транзакция не найдена или произошла ошибка.
    """
    try:
        await transaction_service.delete(db, transaction_id)
        return {"message": "Transaction deleted successfully"}
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при удалении транзакции на стороне API",
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        raise HTTPException(status_code=500, detail="Ошибка при удалении транзакции")