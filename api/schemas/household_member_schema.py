from pydantic import BaseModel, Field
from typing import Optional

class HouseholdMemberBase(BaseModel):
    role: str
    household_id: int = Field(..., gt=0)
    user_id= int = Field(..., gt=0)
    active: bool = True
class HouseholdMemberRead(HouseholdMemberBase):
    id: int

    class Config:
        from_attributes = True

class HouseholdMemberCreate(HouseholdMemberBase):
    pass

class HouseholdMemberUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    description: Optional[str]
    active: Optional[bool]