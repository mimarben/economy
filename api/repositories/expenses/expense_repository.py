"""Expense-specific repository with business logic for expense access."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Expense, User, Source, ExpensesCategory, Account
from repositories.core.base_repository import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    """Repository for Expense entity with custom queries."""

    def __init__(self, db: Session):
        super().__init__(db, Expense)

    def get_by_user(self, user_id: int) -> List[Expense]:
        """Get all expenses for a specific user."""
        stmt = self._base_query().where(Expense.user_id == user_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_category(self, category_id: int) -> List[Expense]:
        """Get all expenses in a specific category."""
        stmt = self._base_query().where(Expense.category_id == category_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_source(self, source_id: int) -> List[Expense]:
        """Get all expenses from a specific source."""
        stmt = self._base_query().where(Expense.source_id == source_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_date_range(self, user_id: int, start_date, end_date) -> List[Expense]:
        """Get expenses for a user within a date range."""
        stmt = self._base_query().where(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        )
        return list(self.db.execute(stmt).scalars().all())

    # Validation methods
    def user_exists(self, user_id: int) -> bool:
        """Check if user exists."""
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def source_exists(self, source_id: int) -> bool:
        """Check if source exists."""
        stmt = select(Source).where(Source.id == source_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def category_exists(self, category_id: int) -> bool:
        """Check if expense category exists."""
        stmt = select(ExpensesCategory).where(ExpensesCategory.id == category_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def account_exists(self, account_id: int) -> bool:
        """Check if account exists."""
        if account_id is None:
            return True  # Account is optional
        stmt = select(Account).where(Account.id == account_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

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
