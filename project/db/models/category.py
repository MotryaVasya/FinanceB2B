from datetime import datetime
from venv import logger
from sqlalchemy import CheckConstraint, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional

from project.db.schemas.category import CategoryOut
from project.db.schemas.transaction import TransactionOut
from project.db.schemas.user import UserOut
from sqlalchemy.sql import text

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firstname: Mapped[str] = mapped_column(String, nullable=False)
    secondname: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tg_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cash: Mapped[float] = mapped_column(Numeric, nullable=False)

    categories: Mapped[list["Category"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def to_pydantic(self):
        return UserOut(
            id=self.id, # TODO поменять просто на id 
            firstname=self.firstname,
            secondname=self.secondname,
            cash=self.cash
        )

class Category(Base):
    __tablename__ = "category"
    __table_args__ = (
        CheckConstraint(
            text("""
                (user_id IS NULL AND name_category IN (
                    'Зарплата', 'Продукты', 'Кафе', 
                    'Досуг', 'Здоровье', 'Транспорт'
                )) 
                OR 
                (user_id IS NOT NULL)
            """),
            name="system_categories_check"
        ),
        CheckConstraint(
            text("""
                NOT (
                    user_id IS NULL 
                    AND name_category NOT IN (
                        'Зарплата', 'Продукты', 'Кафе', 
                        'Досуг', 'Здоровье', 'Транспорт'
                    )
                )
            """),
            name="only_six_system_categories"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_category: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)

    user: Mapped[Optional[User]] = relationship(back_populates="categories")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category", cascade="all, delete-orphan")

    def to_pydantic(self):
        return CategoryOut(
            id=self.id,
            name_category=self.name_category,
            type=self.type,
            user_id=self.user_id
        )

class Transaction(Base):
    __tablename__ = "transit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_sum: Mapped[float] = mapped_column(Numeric, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    category: Mapped["Category"] = relationship(back_populates="transactions")
    user: Mapped["User"] = relationship(back_populates="transactions")

    def to_pydantic(self, category_name: Optional[str] = None) -> TransactionOut:
        return TransactionOut(
            id=self.id,
            description=self.description,
            full_sum=float(self.full_sum),
            date=self.date,  
            category_id=self.category_id,
            user_id=self.user_id,
            category_name=category_name
        )