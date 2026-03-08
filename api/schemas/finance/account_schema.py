from pydantic import BaseModel, Field
from typing import Optional
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
from schemas.audit_schema import AuditFields
class AccountBase(BaseModel):
    name: str
    description: Optional[str] = None
    iban: str
    balance: float
    active: bool = True
    bank_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
class AccountRead(AccountBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    iban: Optional[str]
    balance:  Optional[float]
    active: Optional[bool]

export_schema(AccountBase)
