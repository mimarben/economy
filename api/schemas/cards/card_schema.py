from typing import Optional
from pydantic import BaseModel, Field, field_validator
from models.core.enums import CardTypeEnum
from schemas.core.audit_schema import AuditFields

class CardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    last4: Optional[str] = Field(None, min_length=4, max_length=4)
    type: CardTypeEnum
    active: bool = True
    account_id: int = Field(
        ...,
        gt=0,
        json_schema_extra={
            "ui_type": "select",
            "relation": "account"
        }
    )
    
    @field_validator("last4")
    @classmethod
    def validate_last4(cls, v):
        if v and not v.isdigit():
            raise ValueError("last4 must be numeric")
        return v

class CardRead(CardBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class CardCreate(CardBase):
    pass

class CardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    last4: Optional[str] = Field(None, min_length=4, max_length=4)
    type: Optional[CardTypeEnum] = None
    active: Optional[bool] = None
    account_id: Optional[int] = Field(None, gt=0)