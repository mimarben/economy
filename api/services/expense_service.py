"""Expense service that handles business logic."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from repositories.expense_repository import ExpenseRepository
from schemas.expense_schema import ExpenseCreate, ExpenseRead, ExpenseUpdate
from models.models import Expense


class ExpenseService:
    """
    Service for Expense domain logic.
    
    Responsibilities:
    - Business logic and validation
    - Orchestrating repository operations
    - Transforming between domain and schemas
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ExpenseRepository(db)
    
    def create_expense(self, expense_data: ExpenseCreate) -> ExpenseRead:
        """
        Create a new expense with business rules.
        
        Single Responsibility: Orchestrate expense creation
        """
        # 1. Validate foreign keys (moved from schema)
        is_valid, error = self.repository.validate_foreign_keys(
            user_id=expense_data.user_id,
            source_id=expense_data.source_id,
            category_id=expense_data.category_id,
            account_id=expense_data.account_id
        )
        
        if not is_valid:
            raise ValueError(f"Invalid foreign key: {error}")
        
        # 2. Create expense through repository
        expense = self.repository.create(**expense_data.model_dump())
        
        # 3. Return serialized response
        return ExpenseRead.model_validate(expense)
    
    def get_expense(self, expense_id: int) -> Optional[ExpenseRead]:
        """Get a single expense by ID."""
        expense = self.repository.get_by_id(expense_id)
        if not expense:
            return None
        return ExpenseRead.model_validate(expense)
    
    def get_all_expenses(self) -> List[ExpenseRead]:
        """Get all expenses."""
        expenses = self.repository.get_all()
        return [ExpenseRead.model_validate(exp) for exp in expenses]
    
    def get_user_expenses(self, user_id: int) -> List[ExpenseRead]:
        """Get all expenses for a specific user."""
        expenses = self.repository.get_by_user(user_id)
        return [ExpenseRead.model_validate(exp) for exp in expenses]
    
    def get_expenses_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> List[ExpenseRead]:
        """Get expenses within a date range."""
        expenses = self.repository.get_by_date_range(user_id, start_date, end_date)
        return [ExpenseRead.model_validate(exp) for exp in expenses]
    
    def update_expense(self, expense_id: int, expense_data: ExpenseUpdate) -> Optional[ExpenseRead]:
        """
        Update an expense with business rules.
        
        Note: Foreign keys validation could be added here if needed
        """
        # Get only the fields that were provided (exclude_unset=True)
        update_data = expense_data.model_dump(exclude_unset=True)
        
        expense = self.repository.update(expense_id, **update_data)
        if not expense:
            return None
        
        return ExpenseRead.model_validate(expense)
    
    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense."""
        return self.repository.delete(expense_id)
    
    def calculate_total_expenses(self, user_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        """
        Calculate total expenses for a user.
        
        Example of business logic that goes in the service layer.
        """
        if start_date and end_date:
            expenses = self.repository.get_by_date_range(user_id, start_date, end_date)
        else:
            expenses = self.repository.get_by_user(user_id)
        
        return sum(exp.amount for exp in expenses)
