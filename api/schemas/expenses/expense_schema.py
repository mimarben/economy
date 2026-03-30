from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from models import CurrencyEnum
from utils.schema_exporter import export_schema
from schemas.core.audit_schema import AuditFields


class ExpenseBase(BaseModel):
    """Base schema for Expense aligned with ORM model."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    amount: Decimal = Field(..., gt=0)
    date: date
    currency: CurrencyEnum
    dedup_hash: str = Field(..., min_length=64, max_length=64)
    source_id: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('amount must be greater than 0')
        return v


class ExpenseRead(ExpenseBase, AuditFields):
    """Response schema for Expense."""

    id: int

    class Config:
        from_attributes = True


class ExpenseCreate(ExpenseBase):
    """Schema for creating Expense."""


class ExpenseUpdate(BaseModel):
    """Schema for updating Expense - all fields optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[date] = None
    currency: Optional[CurrencyEnum] = None
    dedup_hash: Optional[str] = Field(None, min_length=64, max_length=64)
    source_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    account_id: Optional[int] = Field(None, gt=0)


class ExpenseDelete(BaseModel):
    pass


export_schema(ExpenseBase)
