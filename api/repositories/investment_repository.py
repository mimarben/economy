"""Repository for Investment entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models.models import Investment


class InvestmentRepository(BaseRepository[Investment]):
    """Repository for Investment with custom queries."""

    def __init__(self, db):
        super().__init__(db, Investment)
