"""Service for Income implementing CRUD operations."""
import re
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from repositories.incomes.income_repository import IncomeRepository
from schemas.incomes.income_schema import IncomeCreate, IncomeRead, IncomeUpdate
from models import Income, CategoryRule, TransactionEnum
from services.core.base_service import BaseService
from services.core.dedup_service import generate_dedup_hash
from services.logs.logger_service import setup_logger

logger = setup_logger("income_service")


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
            with self.db.begin_nested():
                obj = self.repository.create(obj)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            if 'uq_incomes_account_dedup_hash' in str(e.orig):
                raise ValueError("DUPLICATE_TRANSACTION")
            raise

        return IncomeRead.model_validate(obj)

    def update(self, id: int, data: IncomeUpdate) -> Optional[IncomeRead]:
        """
        Update an income. When the user corrects the category and no active
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
                    transaction_type=TransactionEnum.INCOME,
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

            # SAVEPOINT per row: a duplicate only rolls back its own insert.
            try:
                with self.db.begin_nested():
                    obj = self.repository.create(obj)
                created_objects.append(obj)
            except IntegrityError:
                continue

        self.db.commit()
        return [IncomeRead.model_validate(obj) for obj in created_objects]
