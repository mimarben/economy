from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from datetime import datetime
from models.models import User, Account
from sqlalchemy.orm import Session
from flask_babel import _
from models.models import CurrencyEnum
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
class SavingBase(BaseModel):
    description: Optional[str] = None
    amount: float
    date: datetime
    currency: CurrencyEnum
    user_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)

class SavingRead(SavingBase):
    id: int
    class Config:
        from_attributes = True

class SavingCreate(SavingBase):
    @field_validator('account_id', 'user_id')
    @classmethod
    def validate_foreign_key(cls, v, info):
        db = info.context.get('db')
        if not db:
            raise ValueError("DATABASE_NOT_AVAILABLE")
        model_map = {
            'account_id': Account,
            'user_id': User
        }
        model = model_map[info.field_name]
        if not db.query(model).filter(model.id == v).first():
            #raise ValueError(f"{info.field_name.upper()}_NOT_FOUND")
            raise PydanticCustomError("FK_ERROR", f"{info.field_name.upper()}_NOT_FOUND")
        return v

class SavingUpdate(SavingBase):
    description: Optional[str] = None
    amount: Optional[float]
    date: Optional[datetime]
    currency: Optional[CurrencyEnum]
    user_id: Optional[int] = Field(..., gt=0)
    account_id: Optional[int] = Field(..., gt=0)
    # Optional fields

class SavingDelete(BaseModel):
    pass

export_schema(SavingBase)
