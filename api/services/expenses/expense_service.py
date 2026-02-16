"""Expense service implementing CRUD operations with business logic."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from repositories.expenses.expense_repository import ExpenseRepository
from schemas.expenses.expense_schema import ExpenseCreate, ExpenseRead, ExpenseUpdate
from models import Expense
from services.core.base_service import BaseService


class ExpenseService(BaseService[Expense, ExpenseRead, ExpenseCreate, ExpenseUpdate]):
    """
    Service for Expense domain logic.

    Responsibilities:
    - Business logic and validation
    - Orchestrating repository operations
    - Transforming between domain and schemas
    """

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Expense,
            repository=ExpenseRepository(db),
            read_schema=ExpenseRead
        )

    def create(self, data: ExpenseCreate) -> ExpenseRead:
        """Create a new expense with foreign key validation."""
        # Validate foreign keys (moved from schema)
        is_valid, error = self.repository.validate_foreign_keys(
            user_id=data.user_id,
            source_id=data.source_id,
            category_id=data.category_id,
            account_id=data.account_id
        )

        if not is_valid:
            raise ValueError(f"Invalid foreign key: {error}")

        return super().create(data)

    # Domain-specific methods
    def get_by_user(self, user_id: int) -> List[ExpenseRead]:
        """Get all expenses for a specific user."""
        expenses = self.repository.get_by_user(user_id)
        return [ExpenseRead.model_validate(exp) for exp in expenses]

    def get_by_date_range(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[ExpenseRead]:
        """Get expenses within a date range."""
        expenses = self.repository.get_by_date_range(user_id, start_date, end_date)
        return [ExpenseRead.model_validate(exp) for exp in expenses]

    def calculate_total_expenses(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """
        Calculate total expenses for a user.

        Example of business logic that goes in the service layer.
        """
        if start_date and end_date:
            expenses = self.repository.get_by_date_range(user_id, start_date, end_date)
        else:
            expenses = self.repository.get_by_user(user_id)

        return sum(exp.amount for exp in expenses)

