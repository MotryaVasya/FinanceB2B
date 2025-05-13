from datetime import datetime
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from project.db.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from project.db.session import get_db 
from project.services import category_service




router = APIRouter(prefix='/categories', tags=['Categories'])

@router.post('/', response_model=CategoryOut)
async def create_category(user_id: str, data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await category_service.create(user_id, db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии категории на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/{category_id}', response_model=CategoryOut)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    try:
        category = await category_service.get(db, category_id)
        if not category:
            raise HTTPException(404, 'Category not found')
        return category
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении категории на стороне API",
            "category_id": category_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))


@router.get('/', response_model=list[CategoryOut])
async def get_categories(user_id: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        return await category_service.get_all(user_id, db, skip, limit)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении категорий на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
@router.put('/{category_id}', response_model=CategoryOut)
async def update_category(category_id: int, data: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    try:
        category = await category_service.update(db, category_id, data)
        if not category:
            raise HTTPException(404, "Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при обновлении категории на стороне API",
            "data": data,
            "category_id": category_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.delete('/{category_id}')
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    try:
        success = await category_service.delete(db, category_id)
        if not success:
            raise HTTPException(404, "Category not found")
        return {'detail': 'Category deleted'}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при удалении категории на стороне API",
            "category_id": category_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))