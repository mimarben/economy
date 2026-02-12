"""Expense service implementing segregated interfaces following ISP."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from repositories.expense_repository import ExpenseRepository
from schemas.expense_schema import ExpenseCreate, ExpenseRead, ExpenseUpdate
from models.models import Expense
from services.interfaces import ICRUDService


class ExpenseService(ICRUDService[ExpenseRead, ExpenseCreate, ExpenseUpdate]):
    """
    Service for Expense domain logic implementing segregated CRUD interfaces.

    Responsibilities:
    - Business logic and validation
    - Orchestrating repository operations
    - Transforming between domain and schemas
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = ExpenseRepository(db)

    # ICreateService methods
    def create(self, data: ExpenseCreate) -> ExpenseRead:
        """Create a new expense with business rules."""
        # 1. Validate foreign keys (moved from schema)
        is_valid, error = self.repository.validate_foreign_keys(
            user_id=data.user_id,
            source_id=data.source_id,
            category_id=data.category_id,
            account_id=data.account_id
        )

        if not is_valid:
            raise ValueError(f"Invalid foreign key: {error}")

        # 2. Create expense through repository
        expense = self.repository.create(**data.model_dump())

        # 3. Return serialized response
        return ExpenseRead.model_validate(expense)

    # IReadService methods
    def get_by_id(self, id: int) -> Optional[ExpenseRead]:
        """Get a single expense by ID."""
        expense = self.repository.get_by_id(id)
        if not expense:
            return None
        return ExpenseRead.model_validate(expense)

    def get_all(self) -> List[ExpenseRead]:
        """Get all expenses."""
        expenses = self.repository.get_all()
        return [ExpenseRead.model_validate(exp) for exp in expenses]

    # IUpdateService methods
    def update(self, id: int, data: ExpenseUpdate) -> Optional[ExpenseRead]:
        """Update an expense with business rules."""
        # Get only the fields that were provided (exclude_unset=True)
        update_data = data.model_dump(exclude_unset=True)

        expense = self.repository.update(id, **update_data)
        if not expense:
            return None

        return ExpenseRead.model_validate(expense)

    # IDeleteService methods
    def delete(self, id: int) -> bool:
        """Delete an expense."""
        return self.repository.delete(id)

    # ISearchService methods
    def search(self, **filters) -> List[ExpenseRead]:
        """Search expenses by filters."""
        expenses = self.repository.search(**filters)
        return [ExpenseRead.model_validate(exp) for exp in expenses]

    def count(self, **filters) -> int:
        """Count expenses matching filters."""
        return self.repository.count(**filters)

    # Domain-specific methods (optional utility methods)
    def get_by_user(self, user_id: int) -> List[ExpenseRead]:
        """Get all expenses for a specific user."""
        expenses = self.repository.get_by_user(user_id)
        return [ExpenseRead.model_validate(exp) for exp in expenses]

    def get_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> List[ExpenseRead]:
        """Get expenses within a date range."""
        expenses = self.repository.get_by_date_range(user_id, start_date, end_date)
        return [ExpenseRead.model_validate(exp) for exp in expenses]

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

