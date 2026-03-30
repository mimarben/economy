from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema  # Comment translated to English.
from schemas.core.audit_schema import AuditFields
class HouseholdBase(BaseModel):
    name: str
    address: str
    description: Optional[str]
    active: bool = True
class HouseholdRead(HouseholdBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class HouseholdCreate(HouseholdBase):
    pass

class HouseholdUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    description: Optional[str]
    active: Optional[bool]

export_schema(HouseholdBase)
