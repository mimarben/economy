from pydantic import BaseModel
from typing import Optional

class AccountBase(BaseModel):
    name: str
    description: Optional[str] = None
    iban: str
    balance: float
    active: bool = True
class AccountRead(AccountBase):
    id: int

    class Config:
        from_attributes = True

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    iban: Optional[str]
    balance:  Optional[float]
    active: Optional[bool]