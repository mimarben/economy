from pydantic import BaseModel
from typing import Optional

class ExpensesCategoryBase(BaseModel):
    name: str
    address: Optional[str] = None
    description: Optional[str] = None
class ExpensesCategoryRead(ExpensesCategoryBase):
    id: int

    class Config:
        from_attributes = True

class ExpensesCategoryCreate(ExpensesCategoryBase):
    pass

class ExpensesCategoryUpdate(ExpensesCategoryBase):
    pass
