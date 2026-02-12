"""Service for Account implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.account_repository import AccountRepository
from schemas.account_schema import AccountCreate, AccountRead, AccountUpdate
from models.models import Account
from services.interfaces import ICRUDService


class AccountService(ICRUDService[AccountRead, AccountCreate, AccountUpdate]):
    """Service for Account domain logic implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = AccountRepository(db)

    # ICreateService
    def create(self, data: AccountCreate) -> AccountRead:
        """Create a new account."""
        obj = self.repository.create(**data.model_dump())
        return AccountRead.model_validate(obj)

    # IReadService
    def get_by_id(self, id: int) -> Optional[AccountRead]:
        """Get a single account by ID."""
        obj = self.repository.get_by_id(id)
        if not obj:
            return None
        return AccountRead.model_validate(obj)

    def get_all(self) -> List[AccountRead]:
        """Get all accounts."""
        objs = self.repository.get_all()
        return [AccountRead.model_validate(obj) for obj in objs]

    # IUpdateService
    def update(self, id: int, data: AccountUpdate) -> Optional[AccountRead]:
        """Update an account."""
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        if not obj:
            return None
        return AccountRead.model_validate(obj)

    # IDeleteService
    def delete(self, id: int) -> bool:
        """Delete an account."""
        return self.repository.delete(id)

    # ISearchService
    def search(self, **filters) -> List[AccountRead]:
        """Search accounts by filters."""
        objs = self.repository.search(**filters)
        return [AccountRead.model_validate(obj) for obj in objs]

    def count(self, **filters) -> int:
        """Count accounts matching filters."""
        return self.repository.count(**filters)
