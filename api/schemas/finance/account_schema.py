from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field
from models.core.enums import CurrencyEnum
from schemas.core.audit_schema import AuditFields


class AccountBase(BaseModel):
    name: str
    description: Optional[str] = None
    iban: Optional[str] = None
    currency: CurrencyEnum
    balance: Optional[Decimal] = None
    active: bool = True
    bank_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)


class AccountRead(AccountBase, AuditFields):
    id: int

    class Config:
        from_attributes = True


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    iban: Optional[str] = None
    currency: Optional[CurrencyEnum] = None
    balance: Optional[Decimal] = None
    active: Optional[bool] = None
    bank_id: Optional[int] = Field(None, gt=0)
    user_id: Optional[int] = Field(None, gt=0)

