from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
class SourceRead(SourceBase):
    id: int

    class Config:
        from_attributes = True

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]

export_schema(SourceBase)
