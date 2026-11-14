"""Expense service implementing CRUD operations with business logic."""
import re
from typing import Optional, List
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from repositories.expenses.expense_repository import ExpenseRepository
from schemas.expenses.expense_schema import ExpenseCreate, ExpenseRead, ExpenseUpdate
from models import Expense, CategoryRule, TransactionEnum
from services.core.base_service import BaseService
from services.core.dedup_service import generate_dedup_hash
from services.logs.logger_service import setup_logger

logger = setup_logger("expense_service")


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
            with self.db.begin_nested():
                obj = self.repository.create(obj)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
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

            # SAVEPOINT per row: a duplicate only rolls back its own insert.
            try:
                with self.db.begin_nested():
                    obj = self.repository.create(obj)
                created_objects.append(obj)
            except IntegrityError:
                continue

        self.db.commit()
        return [ExpenseRead.model_validate(obj) for obj in created_objects]

    def update(self, id: int, data: ExpenseUpdate) -> Optional[ExpenseRead]:
        """
        Update an expense. When the user corrects the category and no active
        rule covers the description, learn a low-priority rule so future
        imports categorize this description automatically.
        """
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        # Capture BEFORE the update: the ORM identity map means `existing` is
        # the very object super().update() mutates, so comparing afterwards
        # would always see the new value and never trigger learning.
        previous_category_id = existing.category_id
        previous_description = existing.description

        result = super().update(id, data)

        if result is not None:
            update_data = data.model_dump(exclude_unset=True)
            category_changed = (
                "category_id" in update_data
                and update_data["category_id"] is not None
                and update_data["category_id"] != previous_category_id
            )
            if category_changed and previous_description:
                self._learn_category_rule(
                    description=previous_description,
                    category_id=update_data["category_id"],
                    transaction_type=TransactionEnum.EXPENSE,
                )

        return result

    def _learn_category_rule(
        self, description: str, category_id: int, transaction_type
    ) -> None:
        """Create an exact-match rule (low priority) if none covers the description."""
        try:
            from services.rules.categorization_service import CategorizationService

            categorizer = CategorizationService(self.db)
            already_covered = categorizer.categorize_transaction(
                description=description,
                transaction_type=transaction_type.value,
            )
            if already_covered is not None:
                return

            clean_description = description.strip()
            rule = CategoryRule(
                name=f"auto: {clean_description[:60]}",
                pattern=re.escape(clean_description),
                type=transaction_type,
                priority=10,  # learned rules stay below manual ones
                is_active=True,
                category_id=category_id,
            )
            with self.db.begin_nested():
                self.db.add(rule)
                self.db.flush()
            self.db.commit()
            logger.info(
                "Learned category rule for description (category_id=%s)", category_id
            )
        except Exception as e:
            self.db.rollback()
            logger.warning("Could not learn category rule: %s", e)

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
