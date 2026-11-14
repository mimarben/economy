from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from repositories.expenses.expense_repository import ExpenseRepository
from repositories.incomes.income_repository import IncomeRepository
from models import Expense, Income
from services.rules.categorization_service import CategorizationService
from services.core.dedup_service import generate_dedup_hash
from schemas.imports.import_schema import BulkImportRequest
from db.database import atomic
from services.logs.logger_service import setup_logger

logger = setup_logger("import_service")


class ImportService:
    """
    Service handling bulk import orchestration across domains.
    
    Features:
    - Atomic database transaction (all or nothing)
    - Automatic categorization if category_id is null
    - Validation of foreign keys
    - Fallback to AI service for categorization
    """

    def __init__(self, db: Session):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.income_repo = IncomeRepository(db)
        self.categorization_service = CategorizationService(db)

    def import_transactions_atomic(self, data: BulkImportRequest) -> Dict[str, Any]:
        """
        Creates both incomes and expenses in a single atomic database transaction.

        Behavior:
        - If category_id is null and auto_categorize=True → apply rules + AI
        - If categorization fails → category_id remains null
        - If any FK validation fails → raise ValueError (transaction rolls back)
        - All transactions must pass validation or entire import fails

        Args:
            data: BulkImportRequest with expenses and incomes

        Returns:
            Dict with counts of created resources

        Raises:
            ValueError: If any foreign key validation fails
        """
        with atomic(self.db):
            # Step 1: Auto-categorize transactions if needed.
            # Uses the *_with_flags variant so category rules ALSO apply
            # source rules and the ignore_in_analysis flag independently.
            if data.auto_categorize:
                for expense in data.expenses:
                    if expense.category_id is None and expense.description:
                        flags = self.categorization_service.categorize_transaction_with_flags(
                            description=expense.description,
                            transaction_type="expense"
                        )
                        expense.category_id = flags["category_id"]
                        if expense.source_id is None and flags["source_id"]:
                            expense.source_id = flags["source_id"]
                        if flags["ignore_in_analysis"]:
                            expense.ignore_in_analysis = True

                for income in data.incomes:
                    if income.category_id is None and income.description:
                        flags = self.categorization_service.categorize_transaction_with_flags(
                            description=income.description,
                            transaction_type="income"
                        )
                        income.category_id = flags["category_id"]
                        if income.source_id is None and flags["source_id"]:
                            income.source_id = flags["source_id"]
                        if flags["ignore_in_analysis"]:
                            income.ignore_in_analysis = True

            # Step 2: Validate foreign keys for all expenses
            for item in data.expenses:
                # category_id can be None now (needs_review)
                is_valid, error = self.expense_repo.validate_foreign_keys(
                    user_id=item.user_id,
                    source_id=item.source_id,
                    category_id=item.category_id,  # Can be None
                    account_id=item.account_id
                )
                if not is_valid:
                    raise ValueError(f"Expense FK error: {error}")

            # Step 3: Validate foreign keys for all incomes
            for item in data.incomes:
                # category_id can be None now (needs_review)
                is_valid, error = self.income_repo.validate_foreign_keys(
                    source_id=item.source_id,
                    category_id=item.category_id,  # Can be None
                    account_id=item.account_id
                )
                if not is_valid:
                    raise ValueError(f"Income FK error: {error}")

            # Step 4: Deduplicate and insert.
            # Dedup scheme: each row gets a deterministic ordinal = its
            # position within its "family" (same account + date + amount +
            # description) IN THIS FILE. Occurrence 0 keeps the base hash
            # (legacy compatibility); occurrence N is stored as '<base>|<N>'.
            # Bank exports list whole days, so any export covering a day
            # contains ALL of that day's transactions: file position is
            # therefore stable across exports. Re-importing the same file
            # reproduces the same ordinals → everything is a duplicate
            # (idempotency), while a second identical coffee on the same day
            # gets its own slot and is no longer lost.
            inserted_expenses = 0
            inserted_incomes = 0
            duplicates = 0
            expense_family_positions: Dict[Any, int] = {}
            income_family_positions: Dict[Any, int] = {}

            for item in data.expenses:
                date = item.date
                if isinstance(date, str):
                    date = datetime.fromisoformat(date)

                base_hash = generate_dedup_hash(
                    account_id=item.account_id,
                    txn_date=date,
                    amount=item.amount,
                    description=item.description
                )

                family_key = (item.account_id, base_hash)
                position = expense_family_positions.get(family_key, 0)
                expense_family_positions[family_key] = position + 1

                dedup_hash = base_hash if position == 0 else f"{base_hash}|{position}"

                existing = self.expense_repo.get_by_dedup_including_deleted(item.account_id, dedup_hash)
                if existing is not None:
                    if existing.deleted_at is not None:
                        # Soft-deleted row holds the UNIQUE slot: revive it with
                        # the statement's data instead of failing as "duplicate".
                        existing.deleted_at = None
                        existing.name = item.name
                        existing.description = item.description
                        existing.amount = item.amount
                        existing.date = date
                        existing.currency = item.currency
                        existing.user_id = item.user_id
                        existing.source_id = item.source_id
                        existing.category_id = item.category_id
                        existing.card_id = item.card_id
                        existing.ignore_in_analysis = bool(item.ignore_in_analysis)
                        inserted_expenses += 1
                    else:
                        duplicates += 1
                    continue

                obj = Expense(
                    name=item.name,
                    description=item.description,
                    amount=item.amount,
                    date=date,
                    currency=item.currency,
                    user_id=item.user_id,
                    source_id=item.source_id,
                    category_id=item.category_id,
                    account_id=item.account_id,
                    card_id=item.card_id,
                    ignore_in_analysis=bool(item.ignore_in_analysis),
                    dedup_hash=dedup_hash
                )

                try:
                    with self.db.begin_nested():
                        self.db.add(obj)
                        self.db.flush()
                    inserted_expenses += 1
                except IntegrityError as e:
                    if 'uq_expenses_account_dedup_hash' in str(e.orig):
                        duplicates += 1
                    else:
                        # Any other constraint violation (NOT NULL, FK...) must
                        # not be silently counted as a duplicate.
                        raise ValueError(f"Expense constraint error: {e.orig}")

            for item in data.incomes:
                date = item.date
                if isinstance(date, str):
                    date = datetime.fromisoformat(date)

                base_hash = generate_dedup_hash(
                    account_id=item.account_id,
                    txn_date=date,
                    amount=item.amount,
                    description=item.description
                )

                family_key = (item.account_id, base_hash)
                position = income_family_positions.get(family_key, 0)
                income_family_positions[family_key] = position + 1

                dedup_hash = base_hash if position == 0 else f"{base_hash}|{position}"

                existing = self.income_repo.get_by_dedup_including_deleted(item.account_id, dedup_hash)
                if existing is not None:
                    if existing.deleted_at is not None:
                        # Soft-deleted row holds the UNIQUE slot: revive it with
                        # the statement's data instead of failing as "duplicate".
                        existing.deleted_at = None
                        existing.description = item.description
                        existing.amount = item.amount
                        existing.date = date
                        existing.currency = item.currency
                        existing.source_id = item.source_id
                        existing.category_id = item.category_id
                        existing.ignore_in_analysis = bool(item.ignore_in_analysis)
                        inserted_incomes += 1
                    else:
                        duplicates += 1
                    continue

                obj = Income(
                    description=item.description,
                    amount=item.amount,
                    date=date,
                    currency=item.currency,
                    source_id=item.source_id,
                    category_id=item.category_id,
                    account_id=item.account_id,
                    ignore_in_analysis=bool(item.ignore_in_analysis),
                    dedup_hash=dedup_hash
                )

                try:
                    with self.db.begin_nested():
                        self.db.add(obj)
                        self.db.flush()
                    inserted_incomes += 1
                except IntegrityError as e:
                    if 'uq_incomes_account_dedup_hash' in str(e.orig):
                        duplicates += 1
                    else:
                        # Any other constraint violation (NOT NULL, FK...) must
                        # not be silently counted as a duplicate.
                        raise ValueError(f"Income constraint error: {e.orig}")

            total = len(data.expenses) + len(data.incomes)
            logger.info(f"Import complete: {inserted_expenses + inserted_incomes} inserted, {duplicates} duplicates")

            return {
                "inserted": inserted_expenses + inserted_incomes,
                "duplicates": duplicates,
                "total": total
            }
