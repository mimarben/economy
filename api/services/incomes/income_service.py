"""Service for Income implementing CRUD operations."""
from typing import List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from repositories.incomes.income_repository import IncomeRepository
from schemas.incomes.income_schema import IncomeCreate, IncomeRead, IncomeUpdate
from models import Income
from services.core.base_service import BaseService
from services.core.dedup_service import generate_dedup_hash


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

        dedup_hash = generate_dedup_hash(
            account_id=data.account_id,
            txn_date=data.date,
            amount=data.amount,
            description=data.description,
        )

        obj = Income(**self._to_income_model_kwargs(data), dedup_hash=dedup_hash)

        try:
            obj = self.repository.create(obj)
        except IntegrityError as e:
            if 'uq_incomes_account_dedup_hash' in str(e.orig):
                raise ValueError("DUPLICATE_TRANSACTION")
            raise

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

        batch_seen = set()
        created_objects: List[Income] = []

        for item in items:
            dedup_hash = generate_dedup_hash(
                account_id=item.account_id,
                txn_date=item.date,
                amount=item.amount,
                description=item.description,
            )
            key = (item.account_id, dedup_hash)
            if key in batch_seen:
                continue
            batch_seen.add(key)

            if self.repository.exists_by_dedup(item.account_id, dedup_hash):
                continue

            obj = Income(**self._to_income_model_kwargs(item), dedup_hash=dedup_hash)

            try:
                obj = self.repository.create(obj)
                created_objects.append(obj)
            except IntegrityError:
                continue

        return [IncomeRead.model_validate(obj) for obj in created_objects]
