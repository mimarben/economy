"""Segregated service interfaces following ISP - Dependency Inversion Principle."""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = abstractmethod  # Type for read operations
U = abstractmethod  # Type for write operations (DTOs)


class IReadService(ABC, Generic[T]):
    """Interface for read-only service operations."""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Retrieve a single item by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all items."""
        pass


class ISearchService(ABC, Generic[T]):
    """Interface for search/filter operations."""

    @abstractmethod
    def search(self, **filters) -> List[T]:
        """Search items by filters."""
        pass

    @abstractmethod
    def count(self, **filters) -> int:
        """Count items matching filters."""
        pass


class ICreateService(ABC, Generic[U, T]):
    """Interface for create operations - clients depend only on what they create."""

    @abstractmethod
    def create(self, data: U) -> T:
        """Create a new item."""
        pass


class IUpdateService(ABC, Generic[U, T]):
    """Interface for update operations - clients depend only on what they update."""

    @abstractmethod
    def update(self, id: int, data: U) -> Optional[T]:
        """Update an existing item."""
        pass


class IDeleteService(ABC):
    """Interface for delete operations."""

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an item by ID."""
        pass


class ICRUDService(
    IReadService[T],
    ISearchService[T],
    ICreateService[U, T],
    IUpdateService[U, T],
    IDeleteService
):
    """Complete service interface for full CRUD operations."""
    pass
