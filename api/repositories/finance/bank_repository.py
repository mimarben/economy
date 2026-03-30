"""Repository for Bank entity following segregated interfaces."""
from repositories.core.base_repository import BaseRepository
from models import Bank


class BankRepository(BaseRepository[Bank]):
    """Repository for Bank with custom queries."""

    def __init__(self, db):
        super().__init__(db, Bank)

    def find_by_cif(self, cif: str):
        stmt = self._base_query().where(Bank.cif == cif)
        return self.db.execute(stmt).scalar_one_or_none()