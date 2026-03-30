from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema
from schemas.core.audit_schema import AuditFields

class ExpenseCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
class ExpenseCategoryRead(ExpenseCategoryBase, AuditFields):
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
