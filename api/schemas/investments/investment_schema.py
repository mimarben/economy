from typing import Optional
from datetime import date as DateType, datetime

from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from models.core.enums import CurrencyEnum
from schemas.core.audit_schema import AuditFields

# ISIN: 2 letters (country) + 9 alphanumeric (NSIN) + 1 check digit
ISIN_PATTERN = r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$'


class InvestmentBase(BaseModel):
    """Base schema for Investment aligned with ORM model."""

    description: str = Field(..., min_length=1, max_length=500)
    date: DateType = Field(...)
    currency: CurrencyEnum = Field(...)
    amount: Decimal = Field(..., gt=0)
    dedup_hash: str = Field(..., min_length=64, max_length=64)
    isin: Optional[str] = Field(
        None,
        min_length=12,
        max_length=12,
        pattern=ISIN_PATTERN,
        description="ISIN of the fund/ETF/stock this investment tracks (optional)",
    )
    account_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "account"})
    category_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "investment-category"})

    @field_validator('isin', mode='before')
    @classmethod
    def normalize_isin(cls, v: object) -> object:
        """Trim and uppercase so 'ie00b83yjg36 ' is stored as IE00B83YJG36."""
        if isinstance(v, str):
            v = v.strip().upper()
            return v if v else None
        return v


class InvestmentRead(InvestmentBase, AuditFields):
    """Response schema for Investment."""
    id: int

    class Config:
        from_attributes = True


class InvestmentCreate(InvestmentBase):
    """Schema for creating Investment - dedup_hash is generated server-side."""

    dedup_hash: Optional[str] = Field(None, min_length=64, max_length=64)

    @field_validator('date', mode='before')
    @classmethod
    def parse_date_formats(cls, v: object) -> object:
        if not isinstance(v, str):
            return v
        for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(v, fmt).date()
            except ValueError:
                continue
        return v


class InvestmentUpdate(BaseModel):
    """Schema for updating Investment - all fields optional."""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    date: Optional[DateType] = Field(None)
    currency: Optional[CurrencyEnum] = Field(None)
    amount: Optional[Decimal] = Field(None, gt=0)
    dedup_hash: Optional[str] = Field(None, min_length=64, max_length=64)
    isin: Optional[str] = Field(None, min_length=12, max_length=12, pattern=ISIN_PATTERN)
    account_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)

    @field_validator('isin', mode='before')
    @classmethod
    def normalize_isin(cls, v: object) -> object:
        """Trim and uppercase so 'ie00b83yjg36 ' is stored as IE00B83YJG36."""
        if isinstance(v, str):
            v = v.strip().upper()
            return v if v else None
        return v


class InvestmentDelete(BaseModel):
    pass
