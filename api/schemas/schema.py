from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserBase(BaseModel):
    name: str
    surname1: str
    surname2: Optional[str] = None
    dni: str
    email: Optional[EmailStr] = None  # Email validation using Pydantic's `EmailStr`
    telephone: Optional[int] = None  # Telephone is optional

class UserRead(UserBase):
    id: int  # Include the database ID in the read schema

    class Config:
        orm_mode = True  # Enables compatibility with SQLAlchemy models

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname1: Optional[str] = None
    surname2: Optional[str] = None
    dni: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[int] = None


