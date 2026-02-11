"""Income service that handles business logic."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from repositories.income_repository import IncomeRepository
from schemas.income_schema import IncomeCreate, IncomeRead, IncomeUpdate
from models.models import Income


class IncomeService:
    """
    Service for Income domain logic.

    Responsibilities:
    - Business logic and validation
    - Orchestrating repository operations
    - Transforming between domain and schemas
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = IncomeRepository(db)

    def create_income(self, income_data: IncomeCreate) -> IncomeRead:
        """
        Create a new income with business rules.

        Single Responsibility: Orchestrate income creation
        """
        # 1. Validate foreign keys (moved from schema)
        is_valid, error = self.repository.validate_foreign_keys(
            user_id=income_data.user_id,
            source_id=income_data.source_id,
            category_id=income_data.category_id,
            account_id=income_data.account_id
        )

        if not is_valid:
            raise ValueError(f"Invalid foreign key: {error}")

        # 2. Create income through repository
        income = self.repository.create(**income_data.model_dump())

        # 3. Return serialized response
        return IncomeRead.model_validate(income)

    def get_income(self, income_id: int) -> Optional[IncomeRead]:
        """Get a single income by ID."""
        income = self.repository.get_by_id(income_id)
        if not income:
            return None
        return IncomeRead.model_validate(income)

    def get_all_incomes(self) -> List[IncomeRead]:
        """Get all incomes."""
        incomes = self.repository.get_all()
        return [IncomeRead.model_validate(inc) for inc in incomes]

    def get_user_incomes(self, user_id: int) -> List[IncomeRead]:
        """Get all incomes for a specific user."""
        incomes = self.repository.get_by_user(user_id)
        return [IncomeRead.model_validate(inc) for inc in incomes]

    def get_incomes_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> List[IncomeRead]:
        """Get incomes within a date range."""
        incomes = self.repository.get_by_date_range(user_id, start_date, end_date)
        return [IncomeRead.model_validate(inc) for inc in incomes]

    def update_income(self, income_id: int, income_data: IncomeUpdate) -> Optional[IncomeRead]:
        """
        Update an income with business rules.

        Note: Foreign keys validation could be added here if needed
        """
        # Get only the fields that were provided (exclude_unset=True)
        update_data = income_data.model_dump(exclude_unset=True)

        income = self.repository.update(income_id, **update_data)
        if not income:
            return None

        return IncomeRead.model_validate(income)

    def delete_income(self, income_id: int) -> bool:
        """Delete an income."""
        return self.repository.delete(income_id)

    def calculate_total_income(self, user_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        """
        Calculate total income for a user.

        Example of business logic that goes in the service layer.
        """
        if start_date and end_date:
            incomes = self.repository.get_by_date_range(user_id, start_date, end_date)
        else:
            incomes = self.repository.get_by_user(user_id)

        return sum(inc.amount for inc in incomes)
