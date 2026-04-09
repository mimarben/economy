from typing import Optional
from datetime import date as DateType

from decimal import Decimal

from pydantic import BaseModel, Field

from models.core.enums import CurrencyEnum
from schemas.core.audit_schema import AuditFields


class IncomeBase(BaseModel):
    """Base schema for Income aligned with ORM model."""

    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    date: DateType = Field(...)
    currency: CurrencyEnum = Field(...)
    dedup_hash: str = Field(..., min_length=64, max_length=64)
    source_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "source"})
    category_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "income-category"})
    account_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "account"})
    ignore_in_analysis: Optional[bool] = None


class IncomeRead(IncomeBase, AuditFields):
    """Response schema for Income."""
    id: int
    ignore_in_analysis: bool

    class Config:
        from_attributes = True


class IncomeCreate(IncomeBase):
    """Schema for creating Income."""


class IncomeUpdate(BaseModel):
    """Schema for updating Income - all fields optional."""
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[DateType] = Field(None)
    currency: Optional[CurrencyEnum] = Field(None)
    dedup_hash: Optional[str] = Field(None, min_length=64, max_length=64)
    source_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    account_id: Optional[int] = Field(None, gt=0)
    ignore_in_analysis: Optional[bool] = None


class IncomeDelete(BaseModel):
    pass
