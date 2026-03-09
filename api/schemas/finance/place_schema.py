from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
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

export_schema(PlaceBase)
