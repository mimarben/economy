"""Schemas for Instrument."""
from typing import Optional
from pydantic import BaseModel, Field

from schemas.core.audit_schema import AuditFields


class InstrumentBase(BaseModel):
    """Base schema for Instrument aligned with ORM model."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    asset_class: str = Field(..., description="ETF|FUND|STOCK|CRYPTO|BOND|MANAGED_PORTFOLIO|OTHER")
    category_id: int = Field(..., gt=0, description="Reference to investments_categories")
    instrument_type: Optional[str] = Field(None, max_length=32)
    currency: str = Field(..., max_length=8)
    is_active: Optional[bool] = True


class InstrumentRead(InstrumentBase, AuditFields):
    """Response schema for Instrument."""
    id: int

    class Config:
        from_attributes = True


class InstrumentCreate(InstrumentBase):
    """Schema for creating Instrument."""
    pass


class InstrumentUpdate(BaseModel):
    """Schema for updating Instrument - all fields optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    asset_class: Optional[str] = Field(None, description="ETF|FUND|STOCK|CRYPTO|BOND|MANAGED_PORTFOLIO|OTHER")
    category_id: Optional[int] = Field(None, gt=0, description="Reference to investments_categories")
    instrument_type: Optional[str] = Field(None, max_length=32)
    currency: Optional[str] = Field(None, max_length=8)
    is_active: Optional[bool] = None
