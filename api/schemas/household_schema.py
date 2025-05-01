from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
class HouseholdBase(BaseModel):
    name: str
    address: str
    description: Optional[str]
    active: bool = True
class HouseholdRead(HouseholdBase):
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
