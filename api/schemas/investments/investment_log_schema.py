from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from models import ActionEnum
from utils.schema_exporter import export_schema
from schemas.core.audit_schema import AuditFields


class InvestmentLogBase(BaseModel):
    """Base schema for InvestmentLog aligned with ORM model."""

    date: date
    current_value: Decimal = Field(..., gt=0)
    price_per_unit: Optional[Decimal] = Field(None, gt=0)
    units_bought: Optional[Decimal] = Field(None, gt=0)
    action: ActionEnum
    note: Optional[str] = None
    investment_id: int = Field(..., gt=0)


class InvestmentLogRead(InvestmentLogBase, AuditFields):
    """Response schema for InvestmentLog."""
    id: int

    class Config:
        from_attributes = True


class InvestmentLogCreate(InvestmentLogBase):
    """Schema for creating InvestmentLog."""


class InvestmentLogUpdate(BaseModel):
    """Schema for updating InvestmentLog - all fields optional."""

    date: Optional[date] = None
    current_value: Optional[Decimal] = Field(None, gt=0)
    price_per_unit: Optional[Decimal] = Field(None, gt=0)
    units_bought: Optional[Decimal] = Field(None, gt=0)
    action: Optional[ActionEnum] = None
    note: Optional[str] = None
    investment_id: Optional[int] = Field(None, gt=0)


class InvestmentLogDelete(BaseModel):
    pass


export_schema(InvestmentLogBase)
