from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from models import CurrencyEnum
from utils.schema_exporter import export_schema
from schemas.core.audit_schema import AuditFields


class InvestmentBase(BaseModel):
    """Base schema for Investment aligned with ORM model."""

    description: str = Field(..., min_length=1, max_length=500)
    date: date
    currency: CurrencyEnum
    amount: Decimal = Field(..., gt=0)
    dedup_hash: str = Field(..., min_length=64, max_length=64)
    account_id: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)


class InvestmentRead(InvestmentBase, AuditFields):
    """Response schema for Investment."""
    id: int

    class Config:
        from_attributes = True


class InvestmentCreate(InvestmentBase):
    """Schema for creating Investment."""


class InvestmentUpdate(BaseModel):
    """Schema for updating Investment - all fields optional."""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    date: Optional[date] = None
    currency: Optional[CurrencyEnum] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    dedup_hash: Optional[str] = Field(None, min_length=64, max_length=64)
    account_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)


class InvestmentDelete(BaseModel):
    pass


export_schema(InvestmentBase)
