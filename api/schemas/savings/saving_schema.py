from typing import Optional
from datetime import date as DateType

from decimal import Decimal
from pydantic import BaseModel, Field
from models.core.enums import CurrencyEnum
from schemas.core.audit_schema import AuditFields


class SavingBase(BaseModel):
    """Base schema for Saving aligned with ORM model."""

    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    date: DateType = Field(...)
    currency: CurrencyEnum
    account_id: int = Field(..., gt=0)


class SavingRead(SavingBase, AuditFields):
    """Response schema for Saving."""
    id: int

    class Config:
        from_attributes = True


class SavingCreate(SavingBase):
    """Schema for creating Saving."""


class SavingUpdate(BaseModel):
    """Schema for updating Saving - all fields optional."""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[DateType] = Field(None)
    currency: Optional[CurrencyEnum] = None
    account_id: Optional[int] = Field(None, gt=0)


class SavingDelete(BaseModel):
    pass