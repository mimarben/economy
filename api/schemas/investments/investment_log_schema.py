from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models import ActionEnum
from utils.schema_exporter import export_schema
from schemas.core.audit_schema import AuditFields


class InvestmentLogBase(BaseModel):
    """Base schema for InvestmentLog - format validation only."""
    date: datetime
    current_value: float = Field(..., gt=0)
    price_per_unit: Optional[float] = Field(None, gt=0)
    units_bought: Optional[float] = Field(None, gt=0)
    action: ActionEnum
    note: Optional[str] = None
    investment_id: int = Field(..., gt=0)


class InvestmentLogRead(InvestmentLogBase, AuditFields):
    """Response schema for InvestmentLog."""
    id: int

    class Config:
        from_attributes = True


class InvestmentLogCreate(InvestmentLogBase):
    """Schema for creating InvestmentLog - only format validation."""
    pass
    # ✅ NO FK validation here - moved to service layer


class InvestmentLogUpdate(BaseModel):
    """Schema for updating InvestmentLog - all fields optional."""
    date: Optional[datetime] = None
    current_value: Optional[float] = Field(None, gt=0)
    price_per_unit: Optional[float] = Field(None, gt=0)
    units_bought: Optional[float] = Field(None, gt=0)
    action: Optional[ActionEnum] = None
    note: Optional[str] = None
    investment_id: Optional[int] = Field(None, gt=0)


class InvestmentLogDelete(BaseModel):
    pass

export_schema(InvestmentLogBase)
