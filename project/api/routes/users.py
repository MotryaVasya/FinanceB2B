from datetime import datetime
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from project.db.schemas.user import UserCreate, UserUpdate, UserOut
from project.db.session import Session # TODO надо поменять импорт, сессию желательно поставить в другой модуль и сюда импортировать get_db
from services import user_service


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


router = APIRouter(prefix='/users', tags=['Users'])

@router.post('/', response_model=UserOut)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await user_service.create(db, data)
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии пользователя на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/{user_id}', response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await user_service.get(db, user_id)
        if not user:
            raise HTTPException(404, 'User not found')
        return user
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении пользователя на стороне API",
            "user_id": user_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))


# из-за пустово списка который возвраащется при пустой таблице может быть ошибка в response_model что она ожидает в возврате list[UserOut]
@router.get('/', response_model=list[UserOut])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        return await user_service.get_all(db, skip, limit)
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении пользователей на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
@router.put('/{user_id}', response_model=UserOut)
async def update_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    try:
        user = await user_service.update(db, user_id, data)
        if not user:
            raise HTTPException(404, "User not found")
        return user
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при обновлении пользователя на стороне API",
            "data": data,
            "user_id": user_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.delete('/{user_id}')
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        success = await user_service.delete(db, user_id)
        if not success:
            raise HTTPException(404, "User not found")
        return {'detail': 'User deleted'}
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при удалении пользователя на стороне API",
            "user_id": user_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))