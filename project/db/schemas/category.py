from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
    name_category: str
    type: int
    user_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name_category: Optional[str]
    type:  Optional[int]


class CategoryOut(CategoryBase):
    id: int
    
    class Config:
        model_config = ConfigDict(from_attributes=True)