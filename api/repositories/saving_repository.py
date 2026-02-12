"""Repository for Saving entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models.models import Saving


class SavingRepository(BaseRepository[Saving]):
    """Repository for Saving with custom queries."""

    def __init__(self, db):
        super().__init__(db, Saving)
