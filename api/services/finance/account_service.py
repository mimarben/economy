"""Service for Account implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.finance.account_repository import AccountRepository
from schemas.finance.account_schema import AccountBase, AccountCreate, AccountRead, AccountUpdate
from models import Account, AccountUser, User
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

        # Extract user_ids before passing to parent create
        user_ids = data.user_ids
        
        # Remove user_ids from data dict before creating the account
        account_data = data.model_dump(exclude={'user_ids'})

        # Call parent create with cleaned data (AccountBase, no user_ids required)
        created_account = super().create(AccountBase.model_validate(account_data))
        
        # Now add the user associations
        if user_ids:
            self._set_account_users(created_account.id, user_ids)
            # Refresh to include users
            created_account = self.repository.get_by_id(created_account.id)
        
        return created_account

    def update(self, id: int, data: AccountUpdate) -> AccountRead:
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        if data.iban is not None:
            normalized = self._normalize_iban(data.iban)
            if normalized != existing.iban and self.repository.find_by_iban(normalized):
                raise ValueError('Another account with this IBAN already exists')
            data.iban = normalized

        # Extract user_ids if provided
        user_ids = data.user_ids
        
        # Remove user_ids from data dict before updating the account
        if user_ids is not None:
            update_data = data.model_dump(exclude={'user_ids'})
            updated_account = super().update(id, AccountUpdate.model_validate(update_data))
            
            # Update user associations
            self._set_account_users(id, user_ids)
            
            # Refresh to include updated users
            updated_account = self.repository.get_by_id(id)
        else:
            updated_account = super().update(id, data)

        return updated_account

    def _set_account_users(self, account_id: int, user_ids: list[int]) -> None:
        """Set users for an account (replaces existing associations)."""
        # Delete existing associations
        self.db.query(AccountUser).filter(
            AccountUser.account_id == account_id
        ).delete(synchronize_session=False)
        
        # Verify all users exist
        users = self.db.query(User).filter(User.id.in_(user_ids)).all()
        if len(users) != len(user_ids):
            raise ValueError('One or more users do not exist')
        
        # Create new associations
        for user_id in user_ids:
            account_user = AccountUser(account_id=account_id, user_id=user_id)
            self.db.add(account_user)
        
        self.db.flush()

    # ISearchService
    def search(self, **filters) -> list[AccountRead]:
        """Search accounts by filters."""
        objs = self.repository.search(**filters)
        return [AccountRead.model_validate(obj) for obj in objs]

    def count(self, **filters) -> int:
        """Count accounts matching filters."""
        return self.repository.count(**filters)
