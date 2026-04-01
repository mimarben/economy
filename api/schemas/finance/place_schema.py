from typing import Optional
from pydantic import BaseModel
from schemas.core.audit_schema import AuditFields
class PlaceBase(BaseModel):
    name: str
    address: Optional[str] = None
    description: Optional[str] = None
    active: bool = True
class PlaceRead(PlaceBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(PlaceBase):
    pass

