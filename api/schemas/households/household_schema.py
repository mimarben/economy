from typing import Optional
from pydantic import BaseModel
from schemas.core.audit_schema import AuditFields


class HouseholdBase(BaseModel):
    name: str
    address: str
    description: Optional[str] = None
    active: bool = True


class HouseholdRead(HouseholdBase, AuditFields):
    id: int

    class Config:
        from_attributes = True


class HouseholdCreate(HouseholdBase):
    pass


class HouseholdUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None

