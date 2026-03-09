from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models import CurrencyEnum
from utils.schema_exporter import export_schema
from schemas.core.audit_schema import AuditFields


class InvestmentBase(BaseModel):
    """Base schema for Investment - format validation only."""
    name: Optional[str] = None
    date: datetime
    currency: CurrencyEnum
    user_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)


class InvestmentRead(InvestmentBase, AuditFields):
    """Response schema for Investment."""
    id: int

    class Config:
        from_attributes = True


class InvestmentCreate(InvestmentBase):
    """Schema for creating Investment - only format validation."""
    pass
    # ✅ NO FK validation here - moved to service layer


class InvestmentUpdate(BaseModel):
    """Schema for updating Investment - all fields optional."""
    name: Optional[str] = None
    date: Optional[datetime] = None
    currency: Optional[CurrencyEnum] = None
    user_id: Optional[int] = Field(None, gt=0)
    account_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)


class InvestmentDelete(BaseModel):
    pass

export_schema(InvestmentBase)
