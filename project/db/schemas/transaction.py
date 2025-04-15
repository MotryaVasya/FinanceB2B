from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    category_id: int
    fullSum: float
    date: datetime
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    category_id: Optional[int]
    fullSum: Optional[float]
    date: Optional[datetime]
    description: Optional[str] = None

class TransactionOut(TransactionBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True

    # TODO спросить по поводу numeric нам нужен float в пайтоне