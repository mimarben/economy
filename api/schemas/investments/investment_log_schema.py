from typing import Optional
from datetime import date as DateType, datetime

from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from models.core.enums import ActionEnum
from schemas.core.audit_schema import AuditFields


class InvestmentLogBase(BaseModel):
    """Base schema for InvestmentLog aligned with ORM model."""

    date: DateType = Field(...)
    current_value: Optional[Decimal] = Field(None, gt=0)
    price_per_unit: Optional[Decimal] = Field(None, gt=0)
    quantity: Optional[Decimal] = Field(None)
    action: ActionEnum = Field(...)
    note: Optional[str] = Field(None)
    investment_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "investment"})


class InvestmentLogRead(InvestmentLogBase, AuditFields):
    """Response schema for InvestmentLog."""
    id: int

    class Config:
        from_attributes = True


class InvestmentLogCreate(InvestmentLogBase):
    """Schema for creating InvestmentLog."""

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


class InvestmentLogUpdate(BaseModel):
    """Schema for updating InvestmentLog - all fields optional."""

    date: Optional[DateType] = Field(None)
    current_value: Optional[Decimal] = Field(None, gt=0)
    price_per_unit: Optional[Decimal] = Field(None, gt=0)
    quantity: Optional[Decimal] = Field(None)
    action: Optional[ActionEnum] = Field(None)
    note: Optional[str] = Field(None)
    investment_id: Optional[int] = Field(None, gt=0)


class InvestmentLogDelete(BaseModel):
    pass
