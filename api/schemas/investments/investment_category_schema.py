from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema
from schemas.core.audit_schema import AuditFields
class InvestmentCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
class InvestmentCategoryRead(InvestmentCategoryBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class InvestmentCategoryCreate(InvestmentCategoryBase):
    pass

class InvestmentCategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]

export_schema(InvestmentCategoryBase)
