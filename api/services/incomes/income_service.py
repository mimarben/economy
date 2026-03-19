"""Service for Income implementing CRUD operations."""
from typing import List
from sqlalchemy.orm import Session
from repositories.incomes.income_repository import IncomeRepository
from schemas.incomes.income_schema import IncomeCreate, IncomeRead, IncomeUpdate
from models import Income
from services.core.base_service import BaseService


class IncomeService(BaseService[Income, IncomeRead, IncomeCreate, IncomeUpdate]):
    """Service for Income domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Income,
            repository=IncomeRepository(db),
            read_schema=IncomeRead
        )

    @staticmethod
    def _to_income_model_kwargs(data: IncomeCreate) -> dict:
        """
        Keep only fields that exist in Income ORM model.
        This avoids runtime errors with extra schema fields.
        """
        payload = data.model_dump()
        allowed = {"description", "amount", "date", "currency", "source_id", "category_id", "account_id"}
        return {k: v for k, v in payload.items() if k in allowed}

    def create(self, data: IncomeCreate) -> IncomeRead:
        is_valid, error = self.repository.validate_foreign_keys(
            source_id=data.source_id,
            category_id=data.category_id,
            account_id=data.account_id,
        )
        if not is_valid:
            raise ValueError(f"Invalid foreign key: {error}")

        obj = Income(**self._to_income_model_kwargs(data))
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return IncomeRead.model_validate(obj)

    def create_batch_atomic(self, items: List[IncomeCreate]) -> List[IncomeRead]:
        """Create multiple incomes atomically (all-or-nothing)."""
        if not items:
            return []

        for item in items:
            is_valid, error = self.repository.validate_foreign_keys(
                source_id=item.source_id,
                category_id=item.category_id,
                account_id=item.account_id,
            )
            if not is_valid:
                raise ValueError(f"Invalid foreign key: {error}")

        created_objects: List[Income] = []
        with self.db.begin():
            for item in items:
                obj = Income(**self._to_income_model_kwargs(item))
                self.db.add(obj)
                created_objects.append(obj)
            self.db.flush()

        for obj in created_objects:
            self.db.refresh(obj)

        return [IncomeRead.model_validate(obj) for obj in created_objects]
