from typing import Optional
from pydantic import BaseModel, field_validator
from schemas.core.audit_schema import AuditFields


class ImportOriginBase(BaseModel):
    code: str
    name: str
    active: bool = True
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("name cannot be empty")
        return v

class ImportOriginRead(ImportOriginBase, AuditFields):
    id: int

    class Config:
        from_attributes = True


class ImportOriginCreate(ImportOriginBase):
    pass


class ImportOriginUpdate(BaseModel):
    code: Optional[str]
    name: Optional[str]
    active: Optional[bool]