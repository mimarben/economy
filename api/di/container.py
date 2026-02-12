"""Dependency injection container for services following ISP."""
from typing import TypeVar, Generic, Type
from sqlalchemy.orm import Session
from services.interfaces import (
    IReadService, ICreateService, IUpdateService, IDeleteService, ISearchService
)

T = TypeVar('T')
C = TypeVar('C')
U = TypeVar('U')


class ServiceContainer(Generic[T, C, U]):
    """
    Generic dependency injection container for services.

    Provides segregated interface injection to ensure clients depend
    only on interfaces they need (ISP compliance).
    """

    def __init__(self, service_class: Type):
        self.service_class = service_class

    def create_read_service(self, db: Session) -> IReadService[T]:
        """Inject only read service interface."""
        return self.service_class(db)

    def create_write_service(self, db: Session) -> ICreateService[C, T]:
        """Inject only create service interface."""
        return self.service_class(db)

    def create_update_service(self, db: Session) -> IUpdateService[U, T]:
        """Inject only update service interface."""
        return self.service_class(db)

    def create_delete_service(self, db: Session) -> IDeleteService:
        """Inject only delete service interface."""
        return self.service_class(db)

    def create_search_service(self, db: Session) -> ISearchService[T]:
        """Inject only search service interface."""
        return self.service_class(db)

    def create_crud_service(self, db: Session):
        """Inject full CRUD service when needed."""
        return self.service_class(db)
