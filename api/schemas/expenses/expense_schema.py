from typing import Optional
from datetime import date as DateType
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from models.core.enums import CurrencyEnum
from schemas.core.audit_schema import AuditFields


class ExpenseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    amount: Decimal = Field(..., gt=0)
    date: DateType = Field(...)
    currency: CurrencyEnum = Field(...)
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
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[DateType] = Field(None)
    currency: Optional[CurrencyEnum] = None
    dedup_hash: Optional[str] = Field(None, min_length=64, max_length=64)
    source_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    account_id: Optional[int] = Field(None, gt=0)


class ExpenseDelete(BaseModel):
    pass
