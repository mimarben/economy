"""
SourceRule model for mapping category rules to sources.

Each SourceRule associates a CategoryRule with a Source, allowing
automatic source assignment when a rule matches a transaction.
"""

from sqlalchemy import Column, Integer, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin


class SourceRule(TimestampMixin, Base):
    """
    Represents a source suggestion for a categorization rule.

    Allows multiple source suggestions per category rule, providing
    flexibility for rules that match multiple merchant sources.
    """

    __tablename__ = 'source_rules'

    # Primary Key
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

    # Foreign Keys
    category_rule_id = Column(Integer, ForeignKey('category_rules.id'), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False, index=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_source_rules_category_rule_id', 'category_rule_id'),
        Index('idx_source_rules_source_id', 'source_id'),
        Index('idx_source_rules_active', 'is_active'),
    )

    def __repr__(self) -> str:
        return (
            f"<SourceRule(id={self.id}, category_rule_id={self.category_rule_id}, "
            f"source_id={self.source_id}, active={self.is_active})>"
        )
