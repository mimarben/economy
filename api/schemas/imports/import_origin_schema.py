from typing import Optional
from pydantic import BaseModel
from schemas.core.audit_schema import AuditFields


class ImportOriginBase(BaseModel):
    code: str
    name: str
    active: bool = True


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