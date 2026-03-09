from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from utils.schema_exporter import export_schema
from schemas.core.audit_schema import AuditFields


class SavingLogBase(BaseModel):
    """Base schema for SavingLog - format validation only."""
    date: datetime
    amount: float = Field(..., gt=0)
    total_amount: Optional[float] = Field(None, ge=0)
    note: Optional[str] = None
    saving_id: int = Field(..., gt=0)
    source_id: int = Field(..., gt=0)


class SavingLogRead(SavingLogBase, AuditFields):
    """Response schema for SavingLog."""
    id: int

    class Config:
        from_attributes = True


class SavingLogCreate(SavingLogBase):
    """Schema for creating SavingLog - only format validation."""
    pass
    # ✅ NO FK validation here - moved to service layer


class SavingLogUpdate(BaseModel):
    """Schema for updating SavingLog - all fields optional."""
    date: Optional[datetime] = None
    amount: Optional[float] = Field(None, gt=0)
    total_amount: Optional[float] = Field(None, ge=0)
    note: Optional[str] = None
    saving_id: Optional[int] = Field(None, gt=0)
    source_id: Optional[int] = Field(None, gt=0)


class SavingLogDelete(BaseModel):
    pass

export_schema(SavingLogBase)
