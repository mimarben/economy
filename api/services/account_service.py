"""Service for Account implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.account_repository import AccountRepository
from schemas.account_schema import AccountCreate, AccountRead, AccountUpdate
from models.models import Account
from services.base_service import BaseService


class AccountService(BaseService[Account, AccountRead, AccountCreate, AccountUpdate]):
    """Service for Account domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Account,
            repository=AccountRepository(db),
            read_schema=AccountRead
        )

    # ISearchService
    def search(self, **filters) -> List[AccountRead]:
        """Search accounts by filters."""
        objs = self.repository.search(**filters)
        return [AccountRead.model_validate(obj) for obj in objs]

    def count(self, **filters) -> int:
        """Count accounts matching filters."""
        return self.repository.count(**filters)
