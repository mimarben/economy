from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from datetime import datetime
from models import Investment
from flask_babel import _
from models import ActionEnum
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo

class InvestmentLogBase(BaseModel):
    date: datetime
    currentValue: float
    pricePerUnit: float
    unitsBought: float
    action: ActionEnum
    note: str
    investment_id: int = Field(..., gt=0)

class InvestmentLogRead(InvestmentLogBase):
    id: int
    class Config:
        from_attributes = True

class InvestmentLogCreate(InvestmentLogBase):
    @field_validator('investment_id')
    @classmethod
    def validate_foreign_key(cls, v, info):
        db = info.context.get('db')
        if not db:
            raise ValueError("DATABASE_NOT_AVAILABLE")
        model_map = {
            'investment_id': Investment
        }
        model = model_map[info.field_name]
        if not db.query(model).filter(model.id == v).first():
            raise PydanticCustomError("FK_ERROR", f"{info.field_name.upper()}_NOT_FOUND")
        return v

class InvestmentLogUpdate(InvestmentLogBase):
    date: Optional[datetime]
    currentValue: Optional[float]
    pricePerUnit: Optional[float]
    unitsBought: Optional[float]
    action: Optional[ActionEnum]
    note: Optional[str]
    investment_id: Optional[int] = Field(..., gt=0)
    source_id: Optional[int] = Field(..., gt=0)
    # Optional fields

class InvestmentLogDelete(BaseModel):
    pass

export_schema(InvestmentLogBase)
