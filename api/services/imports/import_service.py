from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from repositories.expenses.expense_repository import ExpenseRepository
from repositories.incomes.income_repository import IncomeRepository
from models import Expense, Income
from services.incomes.income_service import IncomeService
from services.category_rules.categorization_service import CategorizationService
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

        # Step 4: Atomic transaction - insert all or nothing
        created_expenses = []
        created_incomes = []
        
        with self.db.begin():
            # Insert expenses
            for item in data.expenses:
                # Parse date if it's a string
                date = item.date
                if isinstance(date, str):
                    date = datetime.fromisoformat(date)
                
                obj = Expense(
                    name=item.name,
                    description=item.description,
                    amount=item.amount,
                    date=date,
                    currency=item.currency,
                    user_id=item.user_id,
                    source_id=item.source_id,
                    category_id=item.category_id,
                    account_id=item.account_id
                )
                self.db.add(obj)
                created_expenses.append(obj)

            # Insert incomes
            for item in data.incomes:
                # Parse date if it's a string
                date = item.date
                if isinstance(date, str):
                    date = datetime.fromisoformat(date)
                
                obj = Income(
                    name=item.name,
                    description=item.description,
                    amount=item.amount,
                    date=date,
                    currency=item.currency,
                    source_id=item.source_id,
                    category_id=item.category_id,
                    account_id=item.account_id
                )
                self.db.add(obj)
                created_incomes.append(obj)

            self.db.flush()

        return {
            "expenses_created": len(created_expenses),
            "incomes_created": len(created_incomes),
            "auto_categorization": data.auto_categorize
        }

