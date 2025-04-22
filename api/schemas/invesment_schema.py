from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from datetime import datetime
from models.models import User, Source, InvestmentsCategory
from flask_babel import _
from models.models import CurrencyEnum
class InvestmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float
    value: float
    date: datetime
    currency: CurrencyEnum
    user_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    
class InvestmentRead(InvestmentBase):
    id: int

    class Config:
        from_attributes = True

class InvestmentCreate(InvestmentBase):
    @field_validator('account_id', 'category_id', 'user_id')
    @classmethod
    def validate_foreign_key(cls, v, info):
        db = info.context.get('db')
        if not db:
            raise ValueError("DATABASE_NOT_AVAILABLE")

        model_map = {
            'category_id': InvestmentsCategory,
            'source_id': Source,
            'user_id': User
        }

        model = model_map[info.field_name]
        if not db.query(model).filter(model.id == v).first():
            #raise ValueError(f"{info.field_name.upper()}_NOT_FOUND")
            raise PydanticCustomError("FK_ERROR", f"{info.field_name.upper()}_NOT_FOUND")
        return v

class InvestmentUpdate(InvestmentBase):
    name: Optional [str]
    description: Optional[str] = None
    amount: Optional [float]
    value: Optional [float]
    date: Optional [datetime]
    currency: Optional [CurrencyEnum]
    user_id: Optional [int] = Field(..., gt=0)
    account_id: Optional [int] = Field(..., gt=0)
    category_id: Optional [int] = Field(..., gt=0)
    # Optional fields

class InvestmentDelete(BaseModel):
    pass

