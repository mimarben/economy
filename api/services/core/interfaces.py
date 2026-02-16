"""Segregated service interfaces following ISP - Dependency Inversion Principle."""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional


TRead = TypeVar("TRead")
TCreate = TypeVar("TCreate")
TUpdate = TypeVar("TUpdate")

class IReadService(ABC, Generic[TRead]):

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[TRead]:
        pass

    @abstractmethod
    def get_all(self) -> List[TRead]:
        pass


class ISearchService(ABC, Generic[TRead]):
    """Interface for search/filter operations."""

    @abstractmethod
    def search(self, **filters) -> List[TRead]:
        """Search items by filters."""
        pass

    @abstractmethod
    def count(self, **filters) -> int:
        """Count items matching filters."""
        pass


class ICreateService(ABC, Generic[TCreate, TRead]):
    """Interface for create operations - clients depend only on what they create."""

    @abstractmethod
    def create(self, data: TCreate) -> TRead:
        """Create a new item."""
        pass


class IUpdateService(ABC, Generic[TUpdate, TRead]):
    """Interface for update operations - clients depend only on what they update."""

    @abstractmethod
    def update(self, id: int, data: TUpdate) -> Optional[TRead]:
        """Update an existing item."""
        pass


class IDeleteService(ABC):
    """Interface for delete operations."""

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an item by ID."""
        pass


class ICRUDService(
    IReadService[TRead],
    ISearchService[TRead],
    ICreateService[TCreate, TRead],
    IUpdateService[TUpdate, TRead],
    IDeleteService
):
    """Complete service interface for full CRUD operations."""
    pass
