"""Repository for Source entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models.models import Source


class SourceRepository(BaseRepository[Source]):
    """Repository for Source with custom queries."""

    def __init__(self, db):
        super().__init__(db, Source)
