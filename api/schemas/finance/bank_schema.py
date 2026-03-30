from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
from schemas.core.audit_schema import AuditFields

class BankBase(BaseModel):
    name: str
    cif: Optional[str] = None
    description: Optional[str] = None
    active: bool = True
class BankRead(BankBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class BankCreate(BankBase):
    pass

class BankUpdate(BaseModel):
    name: Optional[str]
    cif: Optional[str]
    description: Optional[str]
    active: Optional[bool]

export_schema(BankBase)
