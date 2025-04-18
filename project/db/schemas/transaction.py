from pydantic import BaseModel, ConfigDict
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

    class Config:
        model_config = ConfigDict(from_attributes=True)