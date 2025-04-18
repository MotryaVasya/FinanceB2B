from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
    nameCategory: str
    type: int
    user_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    nameCategory: Optional[str]
    type:  Optional[int]


class CategoryOut(CategoryBase):
    id: int
    
    class Config:
        model_config = ConfigDict(from_attributes=True)