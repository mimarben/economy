"""Pydantic schemas for SourceRule model."""

import re
from typing import Optional
from pydantic import BaseModel, field_validator

from schemas.core.audit_schema import AuditFields
from models.core.enums import TransactionEnum


class SourceRuleBase(BaseModel):
    """Base schema for SourceRule."""
    name: str
    pattern: str
    type: TransactionEnum
    priority: int = 100
    is_active: bool = True
    source_id: int

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v: str) -> str:
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}") from e
        return v


class SourceRuleRead(SourceRuleBase, AuditFields):
    """Schema for reading SourceRule."""
    id: int

    class Config:
        from_attributes = True


class SourceRuleCreate(SourceRuleBase):
    """Schema for creating SourceRule."""


class SourceRuleUpdate(BaseModel):
    """Schema for updating SourceRule."""
    name: Optional[str] = None
    pattern: Optional[str] = None
    type: Optional[TransactionEnum] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    source_id: Optional[int] = None

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}") from e
        return v
