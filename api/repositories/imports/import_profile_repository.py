"""Repository for ImportOrigin entity following segregated interfaces."""

from repositories.core.base_repository import BaseRepository
from models.imports import ImportProfile


class ImportProfileRepository(BaseRepository[ImportProfile]):
    """Repository for ImportProfile with custom queries."""

    def __init__(self, db):
        super().__init__(db, ImportProfile)

    def find_by_name(self, name: str):
        stmt = self._base_query().where(ImportProfile.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active(self):
        stmt = self._base_query().where(ImportProfile.active == True)
        return self.db.execute(stmt).scalars().all()