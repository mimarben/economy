"""Repository for Account entity following segregated interfaces."""
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from repositories.core.base_repository import BaseRepository
from models import Account


class AccountRepository(BaseRepository[Account]):
    """Repository for Account with custom queries."""

    def __init__(self, db):
        super().__init__(db, Account)

    def get_all(self, page: int = 1, per_page: int = 50):
        stmt = self._base_query().options(selectinload(Account.users)).offset((page - 1) * per_page).limit(per_page)
        return self.db.execute(stmt).scalars().all()

    def find_by_iban(self, iban: str):
        stmt = self._base_query().where(Account.iban == iban)
        return self.db.execute(stmt).scalar_one_or_none()
