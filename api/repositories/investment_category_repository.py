"""Repository for InvestmentsCategory entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models import InvestmentsCategory


class InvestmentsCategoryRepository(BaseRepository[InvestmentsCategory]):
    """Repository for InvestmentsCategory with custom queries."""

    def __init__(self, db):
        super().__init__(db, InvestmentsCategory)
