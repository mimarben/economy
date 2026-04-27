"""Pydantic schemas for SourceRule model."""

from typing import Optional
from pydantic import BaseModel

from schemas.core.audit_schema import AuditFields


class SourceRuleBase(BaseModel):
    """Base schema for SourceRule."""
    category_rule_id: int
    source_id: int
    is_active: bool = True


class SourceRuleRead(SourceRuleBase, AuditFields):
    """Schema for reading SourceRule."""
    id: int

    class Config:
        from_attributes = True


class SourceRuleCreate(SourceRuleBase):
    """Schema for creating SourceRule."""


class SourceRuleUpdate(BaseModel):
    """Schema for updating SourceRule."""
    category_rule_id: Optional[int] = None
    source_id: Optional[int] = None
    is_active: Optional[bool] = None
