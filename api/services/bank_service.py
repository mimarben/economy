"""Service for Bank implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.bank_repository import BankRepository
from schemas.bank_schema import BankCreate, BankRead, BankUpdate
from models.models import Bank
from services.interfaces import ICRUDService


class BankService(ICRUDService[BankRead, BankCreate, BankUpdate]):
    """Service for Bank domain logic implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = BankRepository(db)

    # ICreateService
    def create(self, data: BankCreate) -> BankRead:
        """Create a new bank."""
        obj = self.repository.create(**data.model_dump())
        return BankRead.model_validate(obj)

    # IReadService
    def get_by_id(self, id: int) -> Optional[BankRead]:
        """Get a single bank by ID."""
        obj = self.repository.get_by_id(id)
        if not obj:
            return None
        return BankRead.model_validate(obj)

    def get_all(self) -> List[BankRead]:
        """Get all banks."""
        objs = self.repository.get_all()
        return [BankRead.model_validate(obj) for obj in objs]

    # IUpdateService
    def update(self, id: int, data: BankUpdate) -> Optional[BankRead]:
        """Update a bank."""
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        if not obj:
            return None
        return BankRead.model_validate(obj)

    # IDeleteService
    def delete(self, id: int) -> bool:
        """Delete a bank."""
        return self.repository.delete(id)

    # ISearchService
    def search(self, **filters) -> List[BankRead]:
        """Search banks by filters."""
        objs = self.repository.search(**filters)
        return [BankRead.model_validate(obj) for obj in objs]

    def count(self, **filters) -> int:
        """Count banks matching filters."""
        return self.repository.count(**filters)
