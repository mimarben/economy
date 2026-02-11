"""Expense-specific repository with business logic for expense access."""
from typing import Optional, List
from sqlalchemy.orm import Session
from models.models import Expense, User, Source, ExpensesCategory, Account
from repositories.base_repository import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    """Repository for Expense entity with custom queries."""
    
    def __init__(self, db: Session):
        super().__init__(db, Expense)
    
    def get_by_user(self, user_id: int) -> List[Expense]:
        """Get all expenses for a specific user."""
        return self.db.query(Expense).filter(Expense.user_id == user_id).all()
    
    def get_by_category(self, category_id: int) -> List[Expense]:
        """Get all expenses in a specific category."""
        return self.db.query(Expense).filter(Expense.category_id == category_id).all()
    
    def get_by_source(self, source_id: int) -> List[Expense]:
        """Get all expenses from a specific source."""
        return self.db.query(Expense).filter(Expense.source_id == source_id).all()
    
    def get_by_date_range(self, user_id: int, start_date, end_date) -> List[Expense]:
        """Get expenses for a user within a date range."""
        return self.db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).all()
    
    # Validation methods - MOVED FROM SCHEMA VALIDATORS
    def user_exists(self, user_id: int) -> bool:
        """Check if user exists."""
        return self.db.query(User).filter(User.id == user_id).first() is not None
    
    def source_exists(self, source_id: int) -> bool:
        """Check if source exists."""
        return self.db.query(Source).filter(Source.id == source_id).first() is not None
    
    def category_exists(self, category_id: int) -> bool:
        """Check if expense category exists."""
        return self.db.query(ExpensesCategory).filter(ExpensesCategory.id == category_id).first() is not None
    
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
