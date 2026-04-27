"""Service for SourceRule domain logic."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import SourceRule, CategoryRule
from repositories.category_rules.source_rule_repository import SourceRuleRepository
from schemas.category_rules.source_rule_schema import (
    SourceRuleRead,
    SourceRuleCreate,
    SourceRuleUpdate,
)
from services.core.base_service import BaseService


class SourceRuleService(BaseService[SourceRule, SourceRuleRead, SourceRuleCreate, SourceRuleUpdate]):
    """Service for managing source rule associations."""

    def __init__(self, db: Session):
        repository = SourceRuleRepository(db)
        super().__init__(
            db=db,
            model=SourceRule,
            repository=repository,
            read_schema=SourceRuleRead
        )

    def get_active_by_category_rule(self, category_rule_id: int) -> List[SourceRuleRead]:
        """Get all active source rules for a category rule."""
        rules = self.repository.get_active_by_category_rule(category_rule_id)
        return [self.read_schema.model_validate(r) for r in rules]

    def _category_rule_exists(self, category_rule_id: int) -> bool:
        """Check if a category rule exists."""
        stmt = select(CategoryRule).where(CategoryRule.id == category_rule_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def _source_exists(self, source_id: int) -> bool:
        """Check if a source exists."""
        from models import Source
        stmt = select(Source).where(Source.id == source_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def create(self, data: SourceRuleCreate) -> SourceRuleRead:
        """Create a new source rule with validation."""
        if not self._category_rule_exists(data.category_rule_id):
            raise ValueError(f"category_rule_id {data.category_rule_id} does not exist")

        if not self._source_exists(data.source_id):
            raise ValueError(f"source_id {data.source_id} does not exist")

        # Check for duplicate
        existing = self.repository.get_by_category_rule_and_source(data.category_rule_id, data.source_id)
        if existing:
            raise ValueError(f"Source rule already exists for category_rule_id {data.category_rule_id} and source_id {data.source_id}")

        return super().create(data)

    def update(self, id: int, data: SourceRuleUpdate) -> Optional[SourceRuleRead]:
        """Update a source rule with validation."""
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        if data.category_rule_id is not None and data.category_rule_id != existing.category_rule_id:
            if not self._category_rule_exists(data.category_rule_id):
                raise ValueError(f"category_rule_id {data.category_rule_id} does not exist")

        if data.source_id is not None and data.source_id != existing.source_id:
            if not self._source_exists(data.source_id):
                raise ValueError(f"source_id {data.source_id} does not exist")

        # Check for duplicate if changing either key
        if data.category_rule_id is not None or data.source_id is not None:
            new_category_rule_id = data.category_rule_id or existing.category_rule_id
            new_source_id = data.source_id or existing.source_id

            if new_category_rule_id != existing.category_rule_id or new_source_id != existing.source_id:
                duplicate = self.repository.get_by_category_rule_and_source(new_category_rule_id, new_source_id)
                if duplicate and duplicate.id != id:
                    raise ValueError(f"Source rule already exists for category_rule_id {new_category_rule_id} and source_id {new_source_id}")

        return super().update(id, data)
