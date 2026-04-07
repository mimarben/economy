from typing import Optional
from datetime import date as DateType

from decimal import Decimal
from pydantic import BaseModel, Field
from schemas.core.audit_schema import AuditFields


class SavingLogBase(BaseModel):
    """Base schema for SavingLog aligned with ORM model."""

    date: DateType = Field(...)
    amount: Decimal = Field(..., gt=0)
    total_amount: Optional[Decimal] = Field(None, ge=0)
    note: Optional[str] = None
    saving_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "saving"})
    source_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "source"})


class SavingLogRead(SavingLogBase, AuditFields):
    """Response schema for SavingLog."""
    id: int

    class Config:
        from_attributes = True


class SavingLogCreate(SavingLogBase):
    """Schema for creating SavingLog."""


class SavingLogUpdate(BaseModel):
    """Schema for updating SavingLog - all fields optional."""

    date: Optional[DateType] = Field(None)
    amount: Optional[Decimal] = Field(None, gt=0)
    total_amount: Optional[Decimal] = Field(None, ge=0)
    note: Optional[str] = Field(None)
    saving_id: Optional[int] = Field(None, gt=0)
    source_id: Optional[int] = Field(None, gt=0)


class SavingLogDelete(BaseModel):
    pass
