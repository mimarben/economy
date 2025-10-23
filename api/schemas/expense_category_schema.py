from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo

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

export_schema(ExpenseCategoryBase)
