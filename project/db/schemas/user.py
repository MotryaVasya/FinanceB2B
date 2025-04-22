from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    firstname: str
    secondname: Optional[str] = None
    tg_id: int
    cash: float

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    cash: float

class UserOut(UserBase):
    id: int

    class Config:
        model_config = ConfigDict(from_attributes=True)


# TODO спросить по поводу numeric нам нужен float в пайтоне 