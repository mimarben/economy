from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from repositories.expenses.expense_repository import ExpenseRepository
from repositories.incomes.income_repository import IncomeRepository
from models import Expense, Income
from services.category_rules.categorization_service import CategorizationService
from services.core.dedup_service import generate_dedup_hash
from schemas.imports.import_schema import BulkImportRequest


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
        
        # Step 1: Auto-categorize transactions if needed
        if data.auto_categorize:
            for expense in data.expenses:
                if expense.category_id is None and expense.description:
                    expense.category_id = self.categorization_service.categorize_transaction(
                        description=expense.description,
                        transaction_type="expense"
                    )
            
            for income in data.incomes:
                if income.category_id is None and income.description:
                    income.category_id = self.categorization_service.categorize_transaction(
                        description=income.description,
                        transaction_type="income"
                    )

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

        # Step 4: Deduplicate and insert
        inserted_expenses = 0
        inserted_incomes = 0
        duplicates = 0
        batch_expense_keys = set()
        batch_income_keys = set()

        for item in data.expenses:
            date = item.date
            if isinstance(date, str):
                date = datetime.fromisoformat(date)

            dedup_hash = generate_dedup_hash(
                account_id=item.account_id,
                txn_date=date,
                amount=item.amount,
                description=item.description
            )

            key = (item.account_id, dedup_hash)
            if key in batch_expense_keys:
                duplicates += 1
                continue
            batch_expense_keys.add(key)

            if self.expense_repo.exists_by_dedup(item.account_id, dedup_hash):
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
                dedup_hash=dedup_hash
            )

            try:
                self.expense_repo.create(obj)
                inserted_expenses += 1
            except IntegrityError:
                duplicates += 1

        for item in data.incomes:
            date = item.date
            if isinstance(date, str):
                date = datetime.fromisoformat(date)

            dedup_hash = generate_dedup_hash(
                account_id=item.account_id,
                txn_date=date,
                amount=item.amount,
                description=item.description
            )

            key = (item.account_id, dedup_hash)
            if key in batch_income_keys:
                duplicates += 1
                continue
            batch_income_keys.add(key)

            if self.income_repo.exists_by_dedup(item.account_id, dedup_hash):
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
                dedup_hash=dedup_hash
            )

            try:
                self.income_repo.create(obj)
                inserted_incomes += 1
            except IntegrityError:
                duplicates += 1

        total = len(data.expenses) + len(data.incomes)

        return {
            "inserted": inserted_expenses + inserted_incomes,
            "duplicates": duplicates,
            "total": total
        }

