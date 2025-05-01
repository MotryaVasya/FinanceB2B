import logging
import httpx
from project.core.request_conf import *

async def create_category(data: dict, params: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{URL}{CATEGORIES}', params=params, json=data)
            response.raise_for_status()
            if response.status_code == 200:
                category = response.json()
                return category
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при создании категории: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при создании категории")

async def get_category(category_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{CATEGORIES}{category_id}')
            response.raise_for_status()
            if response.status_code == 200:
                category = response.json()
                return category
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при получении категории: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получении категории")
    
async def get_categories(user_id: int):
    try:
        async with httpx.AsyncClient() as client:
            params = {'user_id': user_id}
            response = await client.get(f'{URL}{CATEGORIES}', params=params)
            response.raise_for_status()
            if response.status_code == 200:
                category = response.json()
                return category
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при получении категорий: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получении категорий")

async def update_category(category_id: int, data: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(f'{URL}{CATEGORIES}{category_id}', json=data)
            response.raise_for_status()
            if response.status_code == 200:
                category = response.json()
                return category
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при обновлении категории: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при обновлении категории")
    
async def delete_category(category_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f'{URL}{CATEGORIES}{category_id}')
            response.raise_for_status()
            if response.status_code == 200:
                category = response.json()
                return category
    except httpx.HTTPStatusError as e:
        logging.error(f"Произошла ошибка при обновлении категории: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при обновлении категории")