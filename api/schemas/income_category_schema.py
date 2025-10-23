from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
class IncomeCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
class IncomeCategoryRead(IncomeCategoryBase):
    id: int

    class Config:
        from_attributes = True

class IncomeCategoryCreate(IncomeCategoryBase):
    pass

class IncomeCategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]

export_schema(IncomeCategoryBase)
