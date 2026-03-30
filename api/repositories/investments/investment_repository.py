"""Repository for Investment entity following segregated interfaces."""
from repositories.core.base_repository import BaseRepository
from models import Investment


class InvestmentRepository(BaseRepository[Investment]):
    """Repository for Investment with custom queries."""

    def __init__(self, db):
        super().__init__(db, Investment)
    def exists_by_dedup(self, account_id: int, dedup_hash: str) -> bool:
        stmt = self._base_query().where(
            Investment.account_id == account_id,
            Investment.dedup_hash == dedup_hash
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None
