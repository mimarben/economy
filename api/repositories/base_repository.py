"""Base repository with generic CRUD operations implementing segregated interfaces."""
from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.orm import Session
from repositories.interfaces import ICRUDRepository

T = TypeVar('T')


class BaseRepository(ICRUDRepository[T]):
    """Base repository class implementing segregated CRUD interfaces."""

    def __init__(self, db: Session, model: Type[T]):
        """
        Initialize repository with database session and model class.

        Args:
            db: SQLAlchemy database session
            model: The SQLAlchemy model class
        """
        self.db = db
        self.model = model

    # IReadRepository methods
    def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[T]:
        """Get all records."""
        return self.db.query(self.model).all()

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
        """Delete a record by ID."""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    # ISearchRepository methods
    def search(self, **filters) -> List[T]:
        """Search records by filters."""
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()

    def count(self, **filters) -> int:
        """Count records matching filters."""
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.count()
