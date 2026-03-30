from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from models import CurrencyEnum
from utils.schema_exporter import export_schema
from schemas.core.audit_schema import AuditFields


class IncomeBase(BaseModel):
    """Base schema for Income aligned with ORM model."""

    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    date: date
    currency: CurrencyEnum
    dedup_hash: str = Field(..., min_length=64, max_length=64)
    source_id: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)


class IncomeRead(IncomeBase, AuditFields):
    """Response schema for Income."""
    id: int

    class Config:
        from_attributes = True


class IncomeCreate(IncomeBase):
    """Schema for creating Income."""


class IncomeUpdate(BaseModel):
    """Schema for updating Income - all fields optional."""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[date] = None
    currency: Optional[CurrencyEnum] = None
    dedup_hash: Optional[str] = Field(None, min_length=64, max_length=64)
    source_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    account_id: Optional[int] = Field(None, gt=0)


class IncomeDelete(BaseModel):
    pass


export_schema(IncomeBase)
