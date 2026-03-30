"""Service for Account implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.finance.account_repository import AccountRepository
from schemas.finance.account_schema import AccountCreate, AccountRead, AccountUpdate
from models import Account
from services.core.base_service import BaseService


class AccountService(BaseService[Account, AccountRead, AccountCreate, AccountUpdate]):
    """Service for Account domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Account,
            repository=AccountRepository(db),
            read_schema=AccountRead
        )

    @staticmethod
    def _normalize_iban(iban: str | None) -> str | None:
        if iban is None:
            return None
        return iban.replace(' ', '').upper()

    def create(self, data: AccountCreate) -> AccountRead:
        iban = self._normalize_iban(data.iban)
        data.iban = iban

        if iban and self.repository.find_by_iban(iban):
            raise ValueError('Account with this IBAN already exists')

        return super().create(data)

    def update(self, id: int, data: AccountUpdate) -> AccountRead:
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        if data.iban is not None:
            normalized = self._normalize_iban(data.iban)
            if normalized != existing.iban and self.repository.find_by_iban(normalized):
                raise ValueError('Another account with this IBAN already exists')
            data.iban = normalized

        return super().update(id, data)

    # ISearchService
    def search(self, **filters) -> list[AccountRead]:
        """Search accounts by filters."""
        objs = self.repository.search(**filters)
        return [AccountRead.model_validate(obj) for obj in objs]

    def count(self, **filters) -> int:
        """Count accounts matching filters."""
        return self.repository.count(**filters)
