"""Repository for SourceRule model."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import SourceRule
from ..core.base_repository import BaseRepository


class SourceRuleRepository(BaseRepository[SourceRule]):
    """Repository for managing source rule associations."""

    def __init__(self, db: Session):
        super().__init__(db, SourceRule)

    def get_active_by_category_rule(self, category_rule_id: int) -> List[SourceRule]:
        """
        Get all active source rules for a specific category rule.

        Args:
            category_rule_id: The category rule ID

        Returns:
            List of active source rules for the category rule
        """
        stmt = (
            self._base_query()
            .where(SourceRule.is_active == True)
            .where(SourceRule.category_rule_id == category_rule_id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_category_rule_id(self, category_rule_id: int) -> List[SourceRule]:
        """Get all source rules (active and inactive) for a specific category rule."""
        stmt = (
            self._base_query()
            .where(SourceRule.category_rule_id == category_rule_id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_source_id(self, source_id: int) -> List[SourceRule]:
        """Get all source rules associated with a specific source."""
        stmt = (
            self._base_query()
            .where(SourceRule.source_id == source_id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_category_rule_and_source(self, category_rule_id: int, source_id: int) -> Optional[SourceRule]:
        """Get a source rule by category rule and source combination."""
        stmt = (
            self._base_query()
            .where(SourceRule.category_rule_id == category_rule_id)
            .where(SourceRule.source_id == source_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()
