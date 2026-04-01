import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from models.core.enums import UserRoleEnum
from schemas.core.audit_schema import AuditFields


# -------------------------
# Validators
# -------------------------
def check_dni(value: str) -> str:
    pattern = r'^\d{8}[A-Z]$'
    if not re.match(pattern, value):
        raise ValueError('DNI must be 8 digits followed by a letter (e.g., 12345678Z)')

    digits = int(value[:8])
    letters = 'TRWAGMYFPDXBNJZSQVHLCKE'
    expected_letter = letters[digits % 23]
    if value[8] != expected_letter:
        raise ValueError(f'Invalid DNI check letter. Expected {expected_letter}, got {value[8]}')
    return value


def check_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', value):
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', value):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'\d', value):
        raise ValueError('Password must contain at least one number')
    if not re.search(r'[^\w\s]', value):
        raise ValueError('Password must contain at least one symbol')
    return value


# -------------------------
# Base and Read Schemas
# -------------------------
class UserBase(BaseModel):
    name: str
    surname1: str
    surname2: Optional[str] = None
    dni: str
    email: Optional[EmailStr] = None
    active: bool = True
    telephone: Optional[int] = None
    role: UserRoleEnum = UserRoleEnum.USER

    @field_validator('dni')
    @classmethod
    def validate_dni(cls, value: str) -> str:
        return check_dni(value)


class UserRead(UserBase, AuditFields):
    id: int

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        return check_password(value)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname1: Optional[str] = None
    surname2: Optional[str] = None
    dni: Optional[str] = None
    email: Optional[EmailStr] = None
    active: Optional[bool] = None
    telephone: Optional[int] = None
    role: Optional[UserRoleEnum] = None
    password: Optional[str] = None

    @field_validator('dni')
    @classmethod
    def validate_optional_dni(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return check_dni(value)

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return check_password(value)
