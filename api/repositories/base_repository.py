"""Base repository class with common CRUD operations."""
from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Abstract repository for common CRUD operations."""

    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def create(self, **kwargs) -> T:
        """Create and persist a new entity."""
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error creating {self.model.__name__}: {str(e)}")

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def get_all(self) -> List[T]:
        """Get all entities."""
        return self.db.query(self.model).all()

    def update(self, entity_id: int, **kwargs) -> Optional[T]:
        """Update an entity."""
        try:
            instance = self.get_by_id(entity_id)
            if not instance:
                return None

            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            self.db.commit()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error updating {self.model.__name__}: {str(e)}")

    def delete(self, entity_id: int) -> bool:
        """Delete an entity."""
        try:
            instance = self.get_by_id(entity_id)
            if not instance:
                return False

            self.db.delete(instance)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error deleting {self.model.__name__}: {str(e)}")

    def exists(self, entity_id: int) -> bool:
        """Check if entity exists."""
        return self.db.query(self.model).filter(self.model.id == entity_id).first() is not None
