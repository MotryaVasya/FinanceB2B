from datetime import datetime
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from project.db.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut
from project.db.session import Session # TODO надо поменять импорт, сессию желательно поставить в другой модуль и сюда импортировать get_db
from services import transaction_service


#TODO get_db() засунуть в один модуль
async def get_db():
    """
    Генератор сессий для зависимостей FastAPI.
    Автоматически закрывает сессию после завершения запроса.
    """
    async with Session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


router = APIRouter(prefix='/transactions', tags=['Transactions'])

@router.post('/', response_model=TransactionOut)
async def create_transaction(data: TransactionCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await transaction_service.create(db, data)
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии транцакции на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/{transaction_id}', response_model=TransactionOut)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    try:
        transaction = await transaction_service.get(db, transaction_id)
        if not transaction:
            raise HTTPException(404, 'Transaction not found')
        return transaction
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении транзакции на стороне API",
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))


# из-за пустово списка который возвраащется при пустой таблице может быть ошибка в response_model что она ожидает в возврате list[TransactionOut]
@router.get('/', response_model=list[TransactionOut])
async def get_transactions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        return await transaction_service.get_all(db, skip, limit)
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении транзакций на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
@router.put('/{transaction_id}', response_model=TransactionOut)
async def update_transaction(transaction_id: int, data: TransactionUpdate, db: AsyncSession = Depends(get_db)):
    try:
        transaction = await transaction_service.update(db, transaction_id, data)
        if not transaction:
            raise HTTPException(404, "Transaction not found")
        return transaction
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
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при удалении транзакции на стороне API",
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))