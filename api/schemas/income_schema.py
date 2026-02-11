from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from models.models import CurrencyEnum
from flask_babel import _
from utils.schema_exporter import export_schema


class IncomeBase(BaseModel):
    """Base schema for Income - format validation only."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    amount: float = Field(..., gt=0)  # Must be positive
    date: datetime
    currency: CurrencyEnum
    user_id: int = Field(..., gt=0)
    source_id: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    account_id: Optional[int] = Field(None, gt=0)  # Account is optional

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        """Format validation only - no DB queries."""
        if v <= 0:
            raise ValueError('amount must be greater than 0')
        return v


class IncomeRead(IncomeBase):
    """Response schema for Income."""

    id: int

    class Config:
        from_attributes = True


class IncomeCreate(IncomeBase):
    """Schema for creating Income - only format validation."""

    pass
    # ✅ NO FK validation here - moved to service layer
    # ✅ NO DB queries in validators


class IncomeUpdate(BaseModel):
    """Schema for updating Income - all fields optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[datetime] = None
    currency: Optional[CurrencyEnum] = None
    user_id: Optional[int] = Field(None, gt=0)
    source_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    account_id: Optional[int] = Field(None, gt=0)
    source_id: Optional[int]
    category_id: Optional[int]
    account_id: Optional[int]
    # Optional fields

class IncomeDelete(BaseModel):
    pass

export_schema(IncomeBase)

