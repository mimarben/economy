"""Base repository with generic CRUD operations implementing segregated interfaces."""
from datetime import datetime
from typing import TypeVar, Generic, Type, List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from repositories.core.interfaces import ICRUDRepository

T = TypeVar('T')


class BaseRepository(ICRUDRepository[T]):
    """Base repository class implementing segregated CRUD interfaces with SQLAlchemy 2.0 style."""

    def __init__(self, db: Session, model: Type[T]):
        """
        Initialize repository with database session and model class.

        Args:
            db: SQLAlchemy database session
            model: The SQLAlchemy model class
        """
        self.db = db
        self.model = model

    def _base_query(self):
        """Base query that excludes soft-deleted records."""
        stmt = select(self.model)
        if hasattr(self.model, 'deleted_at'):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        return stmt

    # IReadRepository methods
    def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by ID (excluding soft-deleted)."""
        stmt = self._base_query().where(self.model.id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(self, page: int = 1, per_page: int = 50) -> List[T]:
        """Get all records with pagination (excluding soft-deleted)."""
        stmt = self._base_query().offset((page - 1) * per_page).limit(per_page)
        return list(self.db.execute(stmt).scalars().all())

    def get_all_unpaginated(self) -> List[T]:
        """Get all records without pagination (excluding soft-deleted)."""
        stmt = self._base_query()
        return list(self.db.execute(stmt).scalars().all())

    # IWriteRepository methods
    def create(self, obj: T) -> T:
        """Create a new record."""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update a record by ID."""
        obj = self.get_by_id(id)
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        """Soft delete a record by setting deleted_at timestamp."""
        obj = self.get_by_id(id)
        if obj:
            if hasattr(obj, 'deleted_at'):
                obj.deleted_at = datetime.utcnow()
                self.db.commit()
            else:
                # Fallback to hard delete for models without deleted_at
                self.db.delete(obj)
                self.db.commit()
            return True
        return False

    def hard_delete(self, id: int) -> bool:
        """Permanently delete a record from the database."""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    # ISearchRepository methods
    def search(self, **filters) -> List[T]:
        """Search records by filters (excluding soft-deleted)."""
        stmt = self._base_query()
        for key, value in filters.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
        return list(self.db.execute(stmt).scalars().all())

    def count(self, **filters) -> int:
        """Count records matching filters (excluding soft-deleted)."""
        stmt = select(func.count()).select_from(self.model)
        if hasattr(self.model, 'deleted_at'):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        for key, value in filters.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
        return self.db.execute(stmt).scalar_one()
