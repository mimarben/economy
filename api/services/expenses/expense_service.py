"""Expense service implementing CRUD operations with business logic."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from repositories.expenses.expense_repository import ExpenseRepository
from schemas.expenses.expense_schema import ExpenseCreate, ExpenseRead, ExpenseUpdate
from models import Expense
from services.core.base_service import BaseService
from services.core.dedup_service import generate_dedup_hash


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
        """Create a new expense with foreign key validation and dedup protection."""
        is_valid, error = self.repository.validate_foreign_keys(
            user_id=data.user_id,
            source_id=data.source_id,
            category_id=data.category_id,
            account_id=data.account_id
        )
        if not is_valid:
            raise ValueError(f"Invalid foreign key: {error}")

        dedup_hash = generate_dedup_hash(
            account_id=data.account_id,
            txn_date=data.date,
            amount=data.amount,
            description=data.description
        )

        obj = Expense(**data.model_dump(), dedup_hash=dedup_hash)
        try:
            obj = self.repository.create(obj)
        except IntegrityError as e:
            if 'uq_expenses_account_dedup_hash' in str(e.orig):
                raise ValueError("DUPLICATE_TRANSACTION")
            raise

        return ExpenseRead.model_validate(obj)

    def create_batch_atomic(self, items: List[ExpenseCreate]) -> List[ExpenseRead]:
        """
        Create multiple expenses in a single DB transaction with deduplication.

        Duplicates are skipped (same account_id + dedup_hash) and valid rows are persisted.
        """
        if not items:
            return []

        for item in items:
            is_valid, error = self.repository.validate_foreign_keys(
                user_id=item.user_id,
                source_id=item.source_id,
                category_id=item.category_id,
                account_id=item.account_id
            )
            if not is_valid:
                raise ValueError(f"Invalid foreign key: {error}")

        batch_seen = set()
        created_objects: List[Expense] = []

        for item in items:
            dedup_hash = generate_dedup_hash(
                account_id=item.account_id,
                txn_date=item.date,
                amount=item.amount,
                description=item.description
            )

            key = (item.account_id, dedup_hash)
            if key in batch_seen:
                continue

            batch_seen.add(key)

            if self.repository.exists_by_dedup(item.account_id, dedup_hash):
                continue

            obj = Expense(**item.model_dump(), dedup_hash=dedup_hash)

            try:
                obj = self.repository.create(obj)
                created_objects.append(obj)
            except IntegrityError:
                continue

        return [ExpenseRead.model_validate(obj) for obj in created_objects]

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
