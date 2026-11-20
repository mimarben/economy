"""Schemas for InstrumentIdentifier."""
from typing import Optional
from pydantic import BaseModel, Field

from schemas.core.audit_schema import AuditFields


class InstrumentIdentifierBase(BaseModel):
    """Base schema for InstrumentIdentifier aligned with ORM model."""

    instrument_id: int = Field(..., gt=0)
    identifier_type: str = Field(..., description="ISIN|TICKER|SYMBOL|PROVIDER|INTERNAL")
    value: str = Field(..., min_length=1, max_length=64)
    exchange: Optional[str] = Field(None, max_length=16)
    provider: Optional[str] = Field(None, max_length=32)
    is_primary: Optional[bool] = False


class InstrumentIdentifierRead(InstrumentIdentifierBase, AuditFields):
    """Response schema for InstrumentIdentifier."""
    id: int

    class Config:
        from_attributes = True


class InstrumentIdentifierCreate(InstrumentIdentifierBase):
    """Schema for creating InstrumentIdentifier."""
    pass


class InstrumentIdentifierUpdate(BaseModel):
    """Schema for updating InstrumentIdentifier - all fields optional."""

    instrument_id: Optional[int] = Field(None, gt=0)
    identifier_type: Optional[str] = Field(None, description="ISIN|TICKER|SYMBOL|PROVIDER|INTERNAL")
    value: Optional[str] = Field(None, min_length=1, max_length=64)
    exchange: Optional[str] = Field(None, max_length=16)
    provider: Optional[str] = Field(None, max_length=32)
    is_primary: Optional[bool] = None
