from typing import Optional
from datetime import date as DateType

from decimal import Decimal
from pydantic import BaseModel, Field
from models.core.enums import CurrencyEnum
from schemas.core.audit_schema import AuditFields


class InvestmentBase(BaseModel):
    """Base schema for Investment aligned with ORM model."""

    description: str = Field(..., min_length=1, max_length=500)
    date: DateType = Field(...)
    currency: CurrencyEnum = Field(...)
    amount: Decimal = Field(..., gt=0)
    dedup_hash: str = Field(..., min_length=64, max_length=64)
    account_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "account"})
    category_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "investment-category"})


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
    date: Optional[DateType] = Field(None)
    currency: Optional[CurrencyEnum] = Field(None)
    amount: Optional[Decimal] = Field(None, gt=0)
    dedup_hash: Optional[str] = Field(None, min_length=64, max_length=64)
    account_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)


class InvestmentDelete(BaseModel):
    pass
