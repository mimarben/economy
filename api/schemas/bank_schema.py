from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo

class BankBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
class BankRead(BankBase):
    id: int

    class Config:
        from_attributes = True

class BankCreate(BankBase):
    pass

class BankUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]

export_schema(BankBase)
