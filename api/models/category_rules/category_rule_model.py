"""
CategoryRule model for transaction categorization rules.

Stores regex-based rules that can be applied to categorize expenses, incomes, and investments.
Rules are applied in priority order (DESC) when categorizing transactions.
"""

import re
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, Index, CheckConstraint
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import TransactionEnum
from services.logs.logger_service import setup_logger

logger = setup_logger("category_rules")


class CategoryRule(TimestampMixin, Base):
    """
    Represents a categorization rule based on regex patterns.
    
    Used in transaction import workflow:
    1. Extract pattern from DB ordered by priority DESC
    2. Regex match against transaction description (case-insensitive)
    3. If match → return category_id
    4. If no match → fallback to AI service or null
    """
    
    __tablename__ = 'category_rules'
    
    # Primary Key
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    
    # Main fields
    name = Column(String(255), nullable=False)
    pattern = Column(String(1000), nullable=False)  # Regex pattern
    type = Column(SQLEnum(TransactionEnum), nullable=False)  # expense | income | investment
    priority = Column(Integer, nullable=False, default=100)  # Higher = applied first. Must be unique per (type, priority)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Foreign Keys
    category_id = Column(Integer, nullable=False)  # Generic FK to any category
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_category_rules_active_type_priority', 'is_active', 'type', 'priority'),
        Index('idx_category_rules_type_priority', 'type', 'priority'),
    )

    def matches(self, text: str) -> bool:
        """
        Check if the given text matches this rule's regex pattern (case-insensitive).
        
        Args:
            text: Text to match against the pattern
            
        Returns:
            True if the pattern matches, False otherwise
        """
        try:
            return bool(re.search(self.pattern, text, re.IGNORECASE))
        except re.error as e:
            logger.warning("Invalid regex pattern in rule %s: %s", self.id, e)
            return False
    
    def __repr__(self) -> str:
        return (
            f"<CategoryRule(id={self.id}, name='{self.name}', "
            f"type={self.type}, priority={self.priority}, active={self.is_active})>"
        )
