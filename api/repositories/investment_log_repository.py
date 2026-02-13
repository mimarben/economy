"""Repository for InvestmentLog entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models import InvestmentLog


class InvestmentLogRepository(BaseRepository[InvestmentLog]):
    """Repository for InvestmentLog with custom queries."""

    def __init__(self, db):
        super().__init__(db, InvestmentLog)
