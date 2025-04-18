from pydantic import BaseModel
from typing import Optional

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