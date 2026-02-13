"""Repository for Bank entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models import Bank


class BankRepository(BaseRepository[Bank]):
    """Repository for Bank with custom queries."""

    def __init__(self, db):
        super().__init__(db, Bank)
