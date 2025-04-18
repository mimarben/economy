from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from datetime import datetime
from models.models import User, Place, ExpensesCategory
from flask_babel import _

class ExpenseBase(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float
    date: datetime
    category_id: int = Field(..., gt=0)
    place_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    currency: str
    
class ExpenseRead(ExpenseBase):
    id: int

    class Config:
        from_attributes = True

class ExpenseCreate(ExpenseBase):
    @field_validator('category_id', 'place_id', 'user_id')
    @classmethod
    def validate_foreign_key(cls, v, info):
        db = info.context.get('db')
        if not db:
            raise ValueError("DATABASE_NOT_AVAILABLE")

        model_map = {
            'category_id': ExpensesCategory,
            'place_id': Place,
            'user_id': User
        }

        model = model_map[info.field_name]
        if not db.query(model).filter(model.id == v).first():
            #raise ValueError(f"{info.field_name.upper()}_NOT_FOUND")
            raise PydanticCustomError("not_found", f"{info.field_name.upper()}_NOT_FOUND")
        return v

class ExpenseUpdate(ExpenseBase):
    name: Optional[str]
    description: Optional[str] = None
    amount: Optional[float]
    date: Optional[datetime]  # Use str for date representation (ISO format)
    category_id: Optional[int]
    place_id: Optional[int]
    user_id: Optional[int]
    currency: Optional[str]  
    # Optional fields

class ExpenseDelete(BaseModel):
    pass

