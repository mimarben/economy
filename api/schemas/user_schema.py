from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
import re
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
from models import UserRoleEnum

def check_dni(value: str) -> str:
    # DNI format: 8 digits + 1 letter
    pattern = r'^\d{8}[A-Z]$'
    if not re.match(pattern, value):
        raise ValueError('DNI must be 8 digits followed by a letter (e.g., 12345678Z)')

    # Validate check letter
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
class UserBase(BaseModel):
    name: str
    surname1: str
    surname2: Optional[str] = None
    dni: str
    email: Optional[EmailStr] = None
    active: bool = True
    telephone: Optional[int] = None
    role: Optional[UserRoleEnum] = UserRoleEnum.USER
    password: str

    @field_validator('dni')
    def validate_dni(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value  # Return None if dni is not provided
        return check_dni(value)  # Validate the DNI if provided

    @field_validator('password')
    def validate_password(cls, value: str) -> str:
        return check_password(value)
class UserRead(UserBase):
    id: int  # Include the database ID in the read schema

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models

# Schema for creating a user
class UserCreate(UserBase):
  pass

class UserUpdate(UserBase):
  pass

export_schema(UserBase)

