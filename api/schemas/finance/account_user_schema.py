from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from schemas.finance.account_schema import AccountCompact
from schemas.users.user_schema import UserCompact
from schemas.core.audit_schema import AuditFields

class AccountUserBase(BaseModel):
    account_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)

class AccountsUserRead(AccountUserBase, AuditFields):
    id: int
    account: AccountCompact
    user: UserCompact

    class Config:
        from_attributes = True

class AccountUserCreate(AccountUserBase):
    pass

class AccountUserUpdate(BaseModel):
    account_id: Optional[int] = Field(None, gt=0)
    user_id: Optional[int] = Field(None, gt=0)
    

