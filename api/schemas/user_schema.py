from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
import re

from utils.schema_exporter import export_schema  # si guardas la función en otro archivo

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

class UserBase(BaseModel):
    name: str
    surname1: str
    surname2: Optional[str] = None
    dni: str
    email: Optional[EmailStr] = None
    active: bool = True
    telephone: Optional[int] = None

    @field_validator('dni')
    def validate_dni(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value  # Return None if dni is not provided
        return check_dni(value)  # Validate the DNI if provided

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

