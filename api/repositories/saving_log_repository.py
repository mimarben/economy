"""Repository for SavingLog entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models.models import SavingLog


class SavingLogRepository(BaseRepository[SavingLog]):
    """Repository for SavingLog with custom queries."""

    def __init__(self, db):
        super().__init__(db, SavingLog)
