"""Repository for ImportOrigin entity following segregated interfaces."""

from repositories.core.base_repository import BaseRepository
from models.imports import ImportOrigin


class ImportOriginRepository(BaseRepository[ImportOrigin]):
    """Repository for ImportOrigin with custom queries."""

    def __init__(self, db):
        super().__init__(db, ImportOrigin)

    def find_by_code(self, code: str):
        stmt = self._base_query().where(ImportOrigin.code == code)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active(self):
        stmt = self._base_query().where(ImportOrigin.active == True)
        return self.db.execute(stmt).scalars().all()