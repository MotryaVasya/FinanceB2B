from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    firstname: str
    secondname: Optional[str] = None
    cash: float

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    firstname: Optional[str]
    secondname: Optional[str] = None
    cash: float

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True

# TODO спросить по поводу numeric нам нужен float в пайтоне 