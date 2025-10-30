from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from datetime import datetime
from models.models import User, Source,ExpensesCategory, Account
from flask_babel import _
from models.models import CurrencyEnum
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
class ExpenseBase(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float
    date: datetime
    currency: CurrencyEnum
    user_id: int = Field(..., gt=0)
    source_id: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)

class ExpenseRead(ExpenseBase):
    id: int

    class Config:
        from_attributes = True

class ExpenseCreate(ExpenseBase):
    @field_validator('category_id', 'source_id', 'user_id')
    @classmethod
    def validate_foreign_key(cls, v, info):
        db = info.context.get('db')
        if not db:
            raise ValueError("DATABASE_NOT_AVAILABLE")

        model_map = {
            'category_id': ExpensesCategory,
            'source_id': Source,
            'user_id': User,
            'account_id': Account
        }

        model = model_map[info.field_name]
        if not db.query(model).filter(model.id == v).first():
            #raise ValueError(f"{info.field_name.upper()}_NOT_FOUND")
            raise PydanticCustomError("FK_ERROR", f"{info.field_name.upper()}_NOT_FOUND")
        return v

class ExpenseUpdate(ExpenseBase):
    name: Optional[str]
    description: Optional[str] = None
    amount: Optional[float]
    date: Optional[datetime]  # Use str for date representation (ISO format)
    currency: Optional[CurrencyEnum]
    user_id: Optional[int]
    source_id: Optional[int]
    category_id: Optional[int]
    account_id: Optional[int]
    # Optional fields

class ExpenseDelete(BaseModel):
    pass

export_schema(ExpenseBase)
