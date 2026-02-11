"""Income-specific repository with business logic for income access."""
from typing import Optional, List
from sqlalchemy.orm import Session
from models.models import Income, User, Source, IncomesCategory, Account
from repositories.base_repository import BaseRepository


class IncomeRepository(BaseRepository[Income]):
    """Repository for Income entity with custom queries."""

    def __init__(self, db: Session):
        super().__init__(db, Income)

    def get_by_user(self, user_id: int) -> List[Income]:
        """Get all incomes for a specific user."""
        return self.db.query(Income).filter(Income.user_id == user_id).all()

    def get_by_category(self, category_id: int) -> List[Income]:
        """Get all incomes in a specific category."""
        return self.db.query(Income).filter(Income.category_id == category_id).all()

    def get_by_source(self, source_id: int) -> List[Income]:
        """Get all incomes from a specific source."""
        return self.db.query(Income).filter(Income.source_id == source_id).all()

    def get_by_date_range(self, user_id: int, start_date, end_date) -> List[Income]:
        """Get incomes for a user within a date range."""
        return self.db.query(Income).filter(
            Income.user_id == user_id,
            Income.date >= start_date,
            Income.date <= end_date
        ).all()

    # Validation methods - MOVED FROM SCHEMA VALIDATORS
    def user_exists(self, user_id: int) -> bool:
        """Check if user exists."""
        return self.db.query(User).filter(User.id == user_id).first() is not None

    def source_exists(self, source_id: int) -> bool:
        """Check if source exists."""
        return self.db.query(Source).filter(Source.id == source_id).first() is not None

    def category_exists(self, category_id: int) -> bool:
        """Check if income category exists."""
        return self.db.query(IncomesCategory).filter(IncomesCategory.id == category_id).first() is not None

    def account_exists(self, account_id: int) -> bool:
        """Check if account exists."""
        if account_id is None:
            return True  # Account is optional
        return self.db.query(Account).filter(Account.id == account_id).first() is not None

    def validate_foreign_keys(self, user_id: int, source_id: int, category_id: int, account_id: Optional[int]) -> tuple[bool, Optional[str]]:
        """
        Validate all foreign keys at once.
        Returns: (is_valid, error_message)
        """
        if not self.user_exists(user_id):
            return False, "USER_NOT_FOUND"

        if not self.source_exists(source_id):
            return False, "SOURCE_NOT_FOUND"

        if not self.category_exists(category_id):
            return False, "CATEGORY_NOT_FOUND"

        if not self.account_exists(account_id):
            return False, "ACCOUNT_NOT_FOUND"

        return True, None
