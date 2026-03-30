"""Pydantic schemas for CategoryRule model."""

import re
from typing import Optional

from pydantic import BaseModel, field_validator

from models import TransactionEnum
from schemas.core.audit_schema import AuditFields


class CategoryRuleBase(BaseModel):
    """Base schema for CategoryRule."""
    name: str
    pattern: str
    type: TransactionEnum
    priority: int = 100
    is_active: bool = True
    category_id: int

    @field_validator('pattern')
    @classmethod
    def validate_regex_pattern(cls, v: str) -> str:
        """Validate that the pattern is a valid regex."""
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v


class CategoryRuleRead(CategoryRuleBase, AuditFields):
    """Schema for reading CategoryRule."""
    id: int

    class Config:
        from_attributes = True


class CategoryRuleCreate(CategoryRuleBase):
    """Schema for creating CategoryRule."""


class CategoryRuleUpdate(BaseModel):
    """Schema for updating CategoryRule."""
    name: Optional[str] = None
    pattern: Optional[str] = None
    type: Optional[TransactionEnum] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None

    @field_validator('pattern')
    @classmethod
    def validate_regex_pattern(cls, v: Optional[str]) -> Optional[str]:
        """Validate that the pattern is a valid regex if provided."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v
