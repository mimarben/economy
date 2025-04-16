from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExpenseBase(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float
    date: datetime  # Use str for date representation (ISO format)
    category_id: int
    place_id: int
    user_id: int
    currency: str  
    # Optional fields

class ExpenseRead(ExpenseBase):
    id: int

    class Config:
        from_attributes = True

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(ExpenseBase):
    pass

