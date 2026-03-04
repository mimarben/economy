from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models import CurrencyEnum
from utils.schema_exporter import export_schema


class SavingBase(BaseModel):
    """Base schema for Saving - format validation only."""
    description: Optional[str] = Field(None, max_length=500)
    amount: float = Field(..., gt=0)
    date: datetime
    currency: CurrencyEnum
    user_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)


class SavingRead(SavingBase):
    """Response schema for Saving."""
    id: int

    class Config:
        from_attributes = True


class SavingCreate(SavingBase):
    """Schema for creating Saving - only format validation."""
    pass
    # ✅ NO FK validation here - moved to service layer


class SavingUpdate(BaseModel):
    """Schema for updating Saving - all fields optional."""
    description: Optional[str] = Field(None, max_length=500)
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[datetime] = None
    currency: Optional[CurrencyEnum] = None
    user_id: Optional[int] = Field(None, gt=0)
    account_id: Optional[int] = Field(None, gt=0)


class SavingDelete(BaseModel):
    pass

export_schema(SavingBase)
