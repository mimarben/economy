from pydantic import BaseModel
from typing import Dict, List, Optional
from schemas.core.audit_schema import AuditFields


class ImportProfileBase(BaseModel):
    name: str
    header_row_guess: int
    columns: Dict[str, List[str]]
    active: bool = True


class ImportProfileRead(ImportProfileBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class ImportProfileCreate(ImportProfileBase):
    pass

class ImportProfileUpdate(BaseModel):
    name: Optional[str]
    header_row_guess: Optional[int]
    columns: Optional[Dict[str, List[str]]]
    active: Optional[bool]
