"""Repository for Account entity following segregated interfaces."""
from repositories.core.base_repository import BaseRepository
from models import Account


class AccountRepository(BaseRepository[Account]):
    """Repository for Account with custom queries."""

    def __init__(self, db):
        super().__init__(db, Account)

    def find_by_iban(self, iban: str):
        stmt = self._base_query().where(Account.iban == iban)
        return self.db.execute(stmt).scalar_one_or_none()
