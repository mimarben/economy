from typing import Optional
from pydantic import BaseModel, Field
from models.core.enums import RoleEnum
from schemas.core.audit_schema import AuditFields
class HouseholdMemberBase(BaseModel):
    role: RoleEnum
    household_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "household"})
    user_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "user"})
    active: bool = True
class HouseholdMemberRead(HouseholdMemberBase, AuditFields):
    id: int
    class Config:
        from_attributes = True

class HouseholdMemberCreate(HouseholdMemberBase):
    pass

class HouseholdMemberUpdate(BaseModel):
    role: Optional[RoleEnum]
    household_id: Optional[int] = Field(None, gt=0)
    user_id: Optional[int] = Field(None, gt=0)
    active: Optional[bool] = None
