"""Repository for FinancialSummary entity following segregated interfaces."""
from repositories.core.base_repository import BaseRepository
from models import FinancialSummary


class FinancialSummaryRepository(BaseRepository[FinancialSummary]):
    """Repository for FinancialSummary with custom queries."""

    def __init__(self, db):
        super().__init__(db, FinancialSummary)
