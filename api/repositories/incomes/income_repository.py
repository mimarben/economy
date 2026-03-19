"""Repository for Income entity following segregated interfaces."""
from typing import Optional
from sqlalchemy import select
from repositories.core.base_repository import BaseRepository
from models import Income, Source, IncomesCategory, Account


class IncomeRepository(BaseRepository[Income]):
    """Repository for Income with custom queries."""

    def __init__(self, db):
        super().__init__(db, Income)

    def source_exists(self, source_id: int) -> bool:
        stmt = select(Source).where(Source.id == source_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def category_exists(self, category_id: int) -> bool:
        stmt = select(IncomesCategory).where(IncomesCategory.id == category_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def account_exists(self, account_id: Optional[int]) -> bool:
        if account_id is None:
            return True
        stmt = select(Account).where(Account.id == account_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def validate_foreign_keys(
        self,
        source_id: int,
        category_id: int,
        account_id: Optional[int]
    ) -> tuple[bool, Optional[str]]:
        if not self.source_exists(source_id):
            return False, "SOURCE_NOT_FOUND"
        if not self.category_exists(category_id):
            return False, "CATEGORY_NOT_FOUND"
        if not self.account_exists(account_id):
            return False, "ACCOUNT_NOT_FOUND"
        return True, None
