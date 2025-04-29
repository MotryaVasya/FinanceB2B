from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    description: Optional[str] = None
    full_sum: float
    date: datetime
    category_id: int
    user_id: int

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    full_sum: Optional[float]
    date: Optional[datetime]
    category_id: Optional[int]

class TransactionOut(TransactionBase):
    id: int
    date: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()  # Сериализация в ISO формат
        }
    )

    @field_validator('date')
    @classmethod
    def ensure_naive_datetime(cls, v: datetime) -> datetime:
        if v.tzinfo is not None:
            raise ValueError("Timezone-aware datetime not allowed")
        return v

class TransactionCategorySumOut(BaseModel):
    category_id: int
    category_name: str
    total_sum: float
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()  # Сериализация в ISO формат
        }
    )

class TopCategoryOut(BaseModel):
    category_name: str
    full_sum: float
    transaction_history: str # exemple (500+500+500+500)


class TopCategoriesByUserResponse(BaseModel):
    transactions_summary: list[TransactionCategorySumOut]
    top_categories: list[TopCategoryOut]


class CategorySum(BaseModel):
    sum: float
    type: int

class TransactionStatistics(BaseModel):
    from_date: datetime
    to_date: datetime
    income: CategorySum
    expense: CategorySum
    top_categories: list[TopCategoryOut]
    