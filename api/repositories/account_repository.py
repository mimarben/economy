"""Repository for Account entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models import Account


class AccountRepository(BaseRepository[Account]):
    """Repository for Account with custom queries."""

    def __init__(self, db):
        super().__init__(db, Account)
