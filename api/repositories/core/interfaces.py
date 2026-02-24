"""Segregated interfaces for repository operations following ISP."""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')


class IReadRepository(ABC, Generic[T]):
    """Interface for read-only repository operations."""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get a single record by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all records."""
        pass


class IWriteRepository(ABC, Generic[T]):
    """Interface for write operations (create, update, delete)."""

    @abstractmethod
    def create(self, obj: T) -> T:
        """Create a new record."""
        pass

    @abstractmethod
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update a record by ID."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        pass

class ISearchRepository(ABC, Generic[T]):
    """Interface for search/filter operations."""

    @abstractmethod
    def search(self, **filters) -> List[T]:
        """Search records by filters."""
        pass

    @abstractmethod
    def count(self, **filters) -> int:
        """Count records matching filters."""
        pass


class ICRUDRepository(IReadRepository[T], IWriteRepository[T], ISearchRepository[T]):
    """Complete CRUD interface combining read, write, and search operations."""
    pass
