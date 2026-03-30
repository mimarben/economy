"""Repository for Source entity following segregated interfaces."""
from repositories.core.base_repository import BaseRepository
from models import Source


class SourceRepository(BaseRepository[Source]):
    """Repository for Source with custom queries."""

    def __init__(self, db):
        super().__init__(db, Source)

    def get_active_by_type(self, source_type: str):
        """Return first active source of given type (enum value)."""
        stmt = self._base_query().where(Source.type == source_type, Source.active.is_(True))
        return self.db.execute(stmt).scalars().first()

    def get_first_active(self):
        """Fallback to first active source any type."""
        stmt = self._base_query().where(Source.active.is_(True)).order_by(Source.id)
        return self.db.execute(stmt).scalars().first()
