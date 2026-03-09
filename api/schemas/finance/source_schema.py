from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
from models import SourceTypeEnum
from schemas.core.audit_schema import AuditFields
class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
    type: SourceTypeEnum
class SourceRead(SourceBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]
    type: Optional[SourceTypeEnum]


export_schema(SourceBase)
