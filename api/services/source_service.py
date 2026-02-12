"""Service for Source implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.source_repository import SourceRepository
from schemas.source_schema import SourceCreate, SourceRead, SourceUpdate
from models.models import Source
from services.interfaces import ICRUDService


class SourceService(ICRUDService[SourceRead, SourceCreate, SourceUpdate]):
    """Service for Source domain logic implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = SourceRepository(db)

    # ICreateService
    def create(self, data: SourceCreate) -> SourceRead:
        """Create a new source."""
        obj = self.repository.create(**data.model_dump())
        return SourceRead.model_validate(obj)

    # IReadService
    def get_by_id(self, id: int) -> Optional[SourceRead]:
        """Get a single source by ID."""
        obj = self.repository.get_by_id(id)
        if not obj:
            return None
        return SourceRead.model_validate(obj)

    def get_all(self) -> List[SourceRead]:
        """Get all sources."""
        objs = self.repository.get_all()
        return [SourceRead.model_validate(obj) for obj in objs]

    # IUpdateService
    def update(self, id: int, data: SourceUpdate) -> Optional[SourceRead]:
        """Update a source."""
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        if not obj:
            return None
        return SourceRead.model_validate(obj)

    # IDeleteService
    def delete(self, id: int) -> bool:
        """Delete a source."""
        return self.repository.delete(id)

    # ISearchService
    def search(self, **filters) -> List[SourceRead]:
        """Search sources by filters."""
        objs = self.repository.search(**filters)
        return [SourceRead.model_validate(obj) for obj in objs]

    def count(self, **filters) -> int:
        """Count sources matching filters."""
        return self.repository.count(**filters)
