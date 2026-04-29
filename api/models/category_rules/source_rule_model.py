"""
SourceRule model for independent source matching using regex patterns.

Mirrors CategoryRule but assigns a Source instead of a Category.
Runs independently from CategoryRule during transaction categorization.
"""

import re
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum as SQLEnum, Index

from ..core.base import Base, TimestampMixin
from ..core.enums import TransactionEnum
from services.logs.logger_service import setup_logger

logger = setup_logger("source_rules")


class SourceRule(TimestampMixin, Base):
    """
    Regex-based rule that assigns a Source to a transaction.

    Applied independently from CategoryRule: same transaction goes through
    both rule sets in parallel, each in priority DESC order.
    """

    __tablename__ = 'source_rules'

    # Primary Key
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

    # Rule definition (mirrors CategoryRule)
    name = Column(String(255), nullable=False)
    pattern = Column(String(1000), nullable=False)
    type = Column(SQLEnum(TransactionEnum), nullable=False)
    priority = Column(Integer, nullable=False, default=100)
    is_active = Column(Boolean, nullable=False, default=True)

    # Target source
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False, index=True)

    __table_args__ = (
        Index('idx_source_rules_active_type_priority', 'is_active', 'type', 'priority'),
        Index('idx_source_rules_type_priority', 'type', 'priority'),
    )

    def matches(self, text: str) -> bool:
        try:
            return bool(re.search(self.pattern, text, re.IGNORECASE))
        except re.error as e:
            logger.warning("Invalid regex pattern in source rule %s: %s", self.id, e)
            return False

    def __repr__(self) -> str:
        return (
            f"<SourceRule(id={self.id}, name='{self.name}', "
            f"type={self.type}, priority={self.priority}, active={self.is_active})>"
        )
