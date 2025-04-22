from pydantic import BaseModel, Field
from typing import Optional
from models.models import RoleEnum

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