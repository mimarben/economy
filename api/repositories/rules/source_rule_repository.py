"""Repository for SourceRule model."""

from typing import List, Optional
from sqlalchemy.orm import Session

from models import SourceRule, TransactionEnum
from repositories.core.base_repository import BaseRepository


class SourceRuleRepository(BaseRepository[SourceRule]):
    """Repository for managing source rules."""

    def __init__(self, db: Session):
        super().__init__(db, SourceRule)

    def get_active_by_type(self, transaction_type: TransactionEnum) -> List[SourceRule]:
        """Get all active rules for a specific transaction type, ordered by priority DESC."""
        stmt = (
            self._base_query()
            .where(SourceRule.is_active == True)
            .where(SourceRule.type == transaction_type)
            .order_by(SourceRule.priority.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_name(self, name: str) -> Optional[SourceRule]:
        """Get a rule by name."""
        stmt = self._base_query().where(SourceRule.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all_by_type(self, transaction_type: TransactionEnum) -> List[SourceRule]:
        """Get all rules (active and inactive) for a specific type."""
        stmt = (
            self._base_query()
            .where(SourceRule.type == transaction_type)
            .order_by(SourceRule.priority.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_source_id(self, source_id: int) -> List[SourceRule]:
        """Get all rules associated with a specific source."""
        stmt = self._base_query().where(SourceRule.source_id == source_id)
        return list(self.db.execute(stmt).scalars().all())
