from datetime import datetime
from fastapi import status
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from project.db.schemas.transaction import TopCategoriesByUserResponse, TransactionCategorySumOut, TransactionCreate, TransactionUpdate, TransactionOut
from project.db.session import get_db 
from project.services import transaction_service



router = APIRouter(prefix='/transactions', tags=['Transactions'])

@router.post('/', response_model=TransactionOut)
async def create_transaction(data: TransactionCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await transaction_service.create(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии транцакции на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/from_period', response_model=list[TransactionCategorySumOut])
async def get_transactions(from_date: datetime, to_date: datetime, db: AsyncSession = Depends(get_db)):
    try:
        return await transaction_service.get_from_period(db, from_date, to_date)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении транзакций за месяц на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/', response_model=list[TransactionOut])
async def get_transactions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
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

@router.get("/top_categories_by_user", response_model=TopCategoriesByUserResponse)
async def get_top_categories_by_user(from_date: datetime, to_date: datetime, user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await transaction_service.get_top_categories_by_user(db, from_date, to_date, user_id)
    except Exception as e:
        logging.error(f"Ошибка получения топ-3 категорий для пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")

@router.get('/{transaction_id}', response_model=TransactionOut, 
            responses={404: {
                "description": "Transaction not found",}})
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
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

@router.get('/from_month/{month}', response_model=list[TransactionCategorySumOut])
async def get_transactions(month: int, db: AsyncSession = Depends(get_db)):
    try:
        return await transaction_service.get_from_month(db, month)
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
    try:
        transaction = await transaction_service.update(db, transaction_id, data)
        if transaction is None:
            raise HTTPException(404, "Transaction not found")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при обновлении транзакций на стороне API",
            "data": data,
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.delete('/{transaction_id}')
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    try:
        success = await transaction_service.delete(db, transaction_id)
        if not success:
            raise HTTPException(404, "Transaction not found")
        return {'detail': 'Transaction deleted'}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при удалении транзакции на стороне API",
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))