from pydantic import BaseModel
from typing import Optional

class ExpenseCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
class ExpenseCategoryRead(ExpenseCategoryBase):
    id: int

    class Config:
        from_attributes = True

class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass

class ExpenseCategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]