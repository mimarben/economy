"""Schemas for InstrumentComposition."""
from typing import Optional
from pydantic import BaseModel, Field

from schemas.core.audit_schema import AuditFields


class InstrumentCompositionBase(BaseModel):
    """Base schema for InstrumentComposition aligned with ORM model."""

    parent_instrument_id: int = Field(..., gt=0, description="Parent instrument ID")
    child_instrument_id: int = Field(..., gt=0, description="Child instrument ID")
    quantity: float = Field(..., gt=0, description="Quantity of child instruments")
    weight: Optional[float] = Field(None, gt=0, description="Weight as percentage (optional, for analysis)")
    source: Optional[str] = Field(None, max_length=64, description="Source of composition data")
    deleted_at: Optional[str] = Field(None, description="Soft delete timestamp")


class InstrumentCompositionRead(InstrumentCompositionBase, AuditFields):
    """Response schema for InstrumentComposition."""
    id: int
    parent_instrument_id: int
    child_instrument_id: int

    class Config:
        from_attributes = True


class InstrumentCompositionCreate(InstrumentCompositionBase):
    """Schema for creating InstrumentComposition."""
    pass


class InstrumentCompositionUpdate(BaseModel):
    """Schema for updating InstrumentComposition - all fields optional."""

    parent_instrument_id: Optional[int] = Field(None, gt=0, description="Parent instrument ID")
    child_instrument_id: Optional[int] = Field(None, gt=0, description="Child instrument ID")
    quantity: Optional[float] = Field(None, gt=0, description="Quantity of child instruments")
    weight: Optional[float] = Field(None, gt=0, description="Weight as percentage (optional, for analysis)")
    source: Optional[str] = Field(None, max_length=64, description="Source of composition data")
