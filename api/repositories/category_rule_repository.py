"""Repository for CategoryRule model."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import CategoryRule, TransactionEnum
from .core.base_repository import BaseRepository


class CategoryRuleRepository(BaseRepository[CategoryRule]):
    """Repository for managing categorization rules."""

    def __init__(self, db: Session):
        super().__init__(db, CategoryRule)

    def get_active_by_type(self, transaction_type: TransactionEnum) -> List[CategoryRule]:
        """
        Get all active rules for a specific transaction type, ordered by priority DESC.
        
        Args:
            transaction_type: The transaction type (expense, income, investment)
            
        Returns:
            List of active rules sorted by priority (highest first)
        """
        stmt = (
            self._base_query()
            .where(CategoryRule.is_active == True)
            .where(CategoryRule.type == transaction_type)
            .order_by(CategoryRule.priority.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_name(self, name: str) -> Optional[CategoryRule]:
        """Get a rule by name."""
        stmt = self._base_query().where(CategoryRule.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_type_and_priority(self, transaction_type: TransactionEnum, priority: int) -> Optional[CategoryRule]:
        """Get a rule by type and priority combination."""
        stmt = (
            self._base_query()
            .where(CategoryRule.type == transaction_type)
            .where(CategoryRule.priority == priority)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all_by_type(self, transaction_type: TransactionEnum) -> List[CategoryRule]:
        """Get all rules (active and inactive) for a specific type."""
        stmt = (
            self._base_query()
            .where(CategoryRule.type == transaction_type)
            .order_by(CategoryRule.priority.desc())
        )
        return list(self.db.execute(stmt).scalars().all())
