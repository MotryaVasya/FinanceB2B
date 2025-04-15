from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from  models.category import engine
from models.category import User, Category, Transaction

Session = sessionmaker(bind=engine)
session = Session()

# type: 1 - доход, 0 - расход
def add_initial_finanse_database():
    try:
        categories = [
            # 1
            Category(
                nameCategory = "Зарплата",
                type = 1
                # user_id = 
            ),
            # 2
            Category(
                nameCategory = "Продукты",
                type = 0
                # user_id = 
            ),
            # 3
            Category(
                nameCategory = "Кафе",
                type = 0
                # user_id = 
            ),
            # 4
            Category(
                nameCategory = "Досуг",
                type = 0
                # user_id = 
            ),
            # 5
            Category(
                nameCategory = "Здоровье",
                type = 0
                # user_id = 
            ),
            # 6
            Category(
                nameCategory = "Транспорт",
                type = 0
                # user_id = 
            ),
        ]
        session.add_all(categories)
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"Произошла ошибка: {e}")

    finally:
        session.close()    

add_initial_finanse_database()