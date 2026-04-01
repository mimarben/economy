from typing import Optional
from pydantic import BaseModel, Field
from models.core.enums import SourceTypeEnum
from schemas.core.audit_schema import AuditFields
class SourceBase(BaseModel):
    name: str = Field(..., title="Source Name")
    description: Optional[str] = Field(None, title="Description")
    active: bool = Field(True, title="Active")
    type: SourceTypeEnum = Field(..., title="Type")
class SourceRead(SourceBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    name: Optional[str] = Field(None, title="Source Name")
    description: Optional[str] = Field(None, title="Description")
    active: Optional[bool] = Field(None, title="Active")
    type: Optional[SourceTypeEnum] = Field(None, title="Type")
