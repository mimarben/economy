from pydantic import BaseModel, Field
from typing import Optional
from models import RoleEnum
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
class HouseholdMemberBase(BaseModel):
    role: RoleEnum
    household_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    active: bool = True
class HouseholdMemberRead(HouseholdMemberBase):
    id: int
    class Config:
        from_attributes = True

class HouseholdMemberCreate(HouseholdMemberBase):
    pass

class HouseholdMemberUpdate(BaseModel):
    role: Optional[RoleEnum]
    household_id: Optional[int] = Field(..., gt=0)
    user_id:  Optional[int] = Field(..., gt=0)
    active:  Optional[bool]

export_schema(HouseholdMemberBase)
