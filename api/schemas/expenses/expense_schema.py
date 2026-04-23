from typing import Optional
from datetime import date as DateType
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from models.core.enums import CurrencyEnum
from schemas.core.audit_schema import AuditFields


class ExpenseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    amount: Decimal = Field(..., gt=0)
    date: DateType = Field(...)
    currency: CurrencyEnum = Field(...)
    #dedup_hash: str = Field(..., min_length=64, max_length=64)
    source_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "source"})
    category_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "expense-category"})
    account_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "account"})
    ignore_in_analysis: Optional[bool] = None
    card_id: Optional[int] = Field(None, gt=0, json_schema_extra={"ui_type": "select", "relation": "card"})
    is_personal: bool = Field(default=True)
    user_id: Optional[int] = Field(None, gt=0, json_schema_extra={"ui_type": "select", "relation": "user"})
    #ignore_in_analysis: bool = Field(default=False, exclude=True)

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('amount must be greater than 0')
        return v

    @field_validator("card_id")
    @classmethod
    def validate_card(cls, v, info):
        if v is not None:
            account_id = info.data.get("account_id")
            if not account_id:
                raise ValueError("card_id requires account_id")
        return v

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v, info):
        is_personal = info.data.get('is_personal', True)
        if is_personal and v is None:
            raise ValueError('user_id is required for personal expenses')
        return v
class ExpenseRead(ExpenseBase, AuditFields):
    """Response schema for Expense."""
    id: int
    dedup_hash: str
    ignore_in_analysis: bool

    class Config:
        from_attributes = True


class ExpenseCreate(ExpenseBase):
    """Schema for creating Expense."""


class ExpenseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[DateType] = Field(None)
    currency: Optional[CurrencyEnum] = None
    dedup_hash: Optional[str] = Field(None, min_length=64, max_length=64)
    source_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    account_id: Optional[int] = Field(None, gt=0)

    card_id: Optional[int] = Field(None, gt=0)
    ignore_in_analysis: Optional[bool] = None
    is_personal: Optional[bool] = None
    user_id: Optional[int] = Field(None, gt=0)

class ExpenseDelete(BaseModel):
    pass
