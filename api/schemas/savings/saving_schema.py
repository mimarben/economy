from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from models import CurrencyEnum
from utils.schema_exporter import export_schema
from schemas.core.audit_schema import AuditFields


class SavingBase(BaseModel):
    """Base schema for Saving aligned with ORM model."""

    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    date: date
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
    date: Optional[date] = None
    currency: Optional[CurrencyEnum] = None
    account_id: Optional[int] = Field(None, gt=0)


class SavingDelete(BaseModel):
    pass


export_schema(SavingBase)
