from typing import Optional
from pydantic import BaseModel, Field
from schemas.core.audit_schema import AuditFields
class IncomeCategoryBase(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    active: Optional[bool] = None
class IncomeCategoryRead(IncomeCategoryBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class IncomeCategoryCreate(IncomeCategoryBase):
    pass

class IncomeCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    active: Optional[bool] = None
