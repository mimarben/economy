from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from models.core.enums import CurrencyEnum
from schemas.core.audit_schema import AuditFields
from schemas.cards.card_schema import CardRead

class AccountBase(BaseModel):
    name: str
    description: Optional[str] = None
    iban: Optional[str] = None
    currency: CurrencyEnum = Field(...)
    initial_balance: Decimal = Field(
        default=0,
        max_digits=12,
        decimal_places=2
    )
    balance: Optional[Decimal] = Field(
        default=None,
        max_digits=12,
        decimal_places=2
    )
    active: bool = Field(default=True)
    bank_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "bank"})
    user_id: int = Field(..., gt=0, json_schema_extra={"ui_type": "select", "relation": "user"})
    import_origin_id: Optional[int] = Field(None, gt=0, json_schema_extra={"ui_type": "select", "relation": "import-origin"})
    import_profile_id: Optional[int] = Field(None, gt=0, json_schema_extra={"ui_type": "select", "relation": "import-profile"})
    
    @field_validator("balance")
    @classmethod
    def validate_balance(cls, v):
        return v  # no restrinjas (puede ser negativo en cuentas reales)

    @field_validator("iban")
    @classmethod
    def validate_iban(cls, v):
        if v and len(v.replace(" ", "")) < 15:
            raise ValueError("Invalid IBAN")
class AccountRead(AccountBase, AuditFields):
    id: int
    cards: List[CardRead] = Field(default_factory=list)
    class Config:
        from_attributes = True


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    iban: Optional[str] = None
    currency: Optional[CurrencyEnum] = None
    balance: Optional[Decimal] = None
    active: Optional[bool] = None
    bank_id: Optional[int] = Field(None, gt=0)
    user_id: Optional[int] = Field(None, gt=0)
    import_origin_id: Optional[int] = Field(None, gt=0)
    import_profile_id: Optional[int] = Field(None, gt=0)
