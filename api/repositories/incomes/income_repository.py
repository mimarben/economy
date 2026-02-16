"""Repository for Income entity following segregated interfaces."""
from repositories.core.base_repository import BaseRepository
from models import Income


class IncomeRepository(BaseRepository[Income]):
    """Repository for Income with custom queries."""

    def __init__(self, db):
        super().__init__(db, Income)
