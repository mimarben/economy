from pydantic import BaseModel
from typing import Optional

class ExpensesCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
class ExpensesCategoryRead(ExpensesCategoryBase):
    id: int

    class Config:
        from_attributes = True

class ExpensesCategoryCreate(ExpensesCategoryBase):
    pass

class ExpensesCategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]