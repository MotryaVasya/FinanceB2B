from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
    nameCategory: str
    type: int

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    nameCategory: Optional[str]
    type:  Optional[int]


class CategoryOut(CategoryBase):
    id: int

    class Config:
        orm_mode = True