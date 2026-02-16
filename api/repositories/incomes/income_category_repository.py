"""Repository for IncomesCategory entity following segregated interfaces."""
from repositories.core.base_repository import BaseRepository
from models import IncomesCategory


class IncomesCategoryRepository(BaseRepository[IncomesCategory]):
    """Repository for IncomesCategory with custom queries."""

    def __init__(self, db):
        super().__init__(db, IncomesCategory)
