from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from datetime import datetime
from models.models import Saving
from flask_babel import _
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo

class SavingLogBase(BaseModel):
    date: datetime
    amount: float
    total_amount: float
    note: str
    saving_id: int = Field(..., gt=0)
    source_id: int = Field(..., gt=0)
class SavingLogRead(SavingLogBase):
    id: int
    class Config:
        from_attributes = True

class SavingLogCreate(SavingLogBase):
    @field_validator('saving_id')
    @classmethod
    def validate_foreign_key(cls, v, info):
        db = info.context.get('db')
        if not db:
            raise ValueError("DATABASE_NOT_AVAILABLE")
        model_map = {
            'saving_id': Saving
        }
        model = model_map[info.field_name]
        if not db.query(model).filter(model.id == v).first():
            raise PydanticCustomError("FK_ERROR", f"{info.field_name.upper()}_NOT_FOUND")
        return v

class SavingLogUpdate(SavingLogBase):
    date: Optional[datetime]
    amount: Optional[float]
    total_amount: Optional[float]
    note: Optional[str]
    saving_id: Optional[int]
    source_id: Optional[int] = Field(..., gt=0)
    # Optional fields

class SavingLogDelete(BaseModel):
    pass
export_schema(SavingLogBase)
