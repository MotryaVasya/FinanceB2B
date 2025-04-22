from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.future import select
from project.db.models.category import Base, Category
from sqlalchemy.exc import SQLAlchemyError
import asyncio
from project.core.config import config

async_engine = create_async_engine(config.database_url, echo=True)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

            

async def add_initial_finanse_database():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Category).where(Category.user_id.is_(None)))
            existing_categories = result.scalars().all()
            
            if not existing_categories:
                categories = [
                    Category(name_category="Зарплата", type=1),
                    Category(name_category="Продукты", type=0),
                    Category(name_category="Кафе", type=0),
                    Category(name_category="Досуг", type=0),
                    Category(name_category="Здоровье", type=0),
                    Category(name_category="Транспорт", type=0),
                ]
                
                session.add_all(categories)
                await session.commit()
                print("Начальные категории успешно добавлены")
            else:
                print("Категории уже существуют в базе данных")
                
        except SQLAlchemyError as e:
            print(f"Произошла ошибка: {e}")
            await session.rollback()
            raise



async def init_db_on_start_up():
    await init_db()
    await add_initial_finanse_database()


# Для тестирования
# async def main():
#     await init_db_on_start_up()

# if __name__ == "__main__":
#     asyncio.run(main())