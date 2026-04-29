"""Service for SourceRule domain logic."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import SourceRule
from repositories.rules.source_rule_repository import SourceRuleRepository
from schemas.rules.source_rule_schema import (
    SourceRuleRead,
    SourceRuleCreate,
    SourceRuleUpdate,
)
from services.core.base_service import BaseService


class SourceRuleService(BaseService[SourceRule, SourceRuleRead, SourceRuleCreate, SourceRuleUpdate]):
    """Service for managing source rules."""

    def __init__(self, db: Session):
        repository = SourceRuleRepository(db)
        super().__init__(
            db=db,
            model=SourceRule,
            repository=repository,
            read_schema=SourceRuleRead
        )

    def get_active_by_type(self, transaction_type: str) -> List[SourceRuleRead]:
        """Get all active source rules for a transaction type."""
        from models.core.enums import TransactionEnum
        try:
            enum_type = TransactionEnum(transaction_type)
        except ValueError:
            raise ValueError(f"Invalid transaction type: {transaction_type}")
        rules = self.repository.get_active_by_type(enum_type)
        return [self.read_schema.model_validate(r) for r in rules]

    def _source_exists(self, source_id: int) -> bool:
        from models import Source
        stmt = select(Source).where(Source.id == source_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def create(self, data: SourceRuleCreate) -> SourceRuleRead:
        if not self._source_exists(data.source_id):
            raise ValueError(f"source_id {data.source_id} does not exist")
        return super().create(data)

    def update(self, id: int, data: SourceRuleUpdate) -> Optional[SourceRuleRead]:
        existing = self.repository.get_by_id(id)
        if not existing:
            return None
        if data.source_id is not None and not self._source_exists(data.source_id):
            raise ValueError(f"source_id {data.source_id} does not exist")
        return super().update(id, data)
