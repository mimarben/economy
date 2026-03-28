"""Service for CategoryRule domain logic and transaction categorization."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import CategoryRule, TransactionEnum
from repositories.category_rules.category_rule_repository import CategoryRuleRepository
from schemas.category_rules.category_rule_schema import (
    CategoryRuleRead,
    CategoryRuleCreate,
    CategoryRuleUpdate,
)
from services.core.base_service import BaseService


class CategoryRuleService(BaseService[CategoryRule, CategoryRuleRead, CategoryRuleCreate, CategoryRuleUpdate]):
    """Service for managing categorization rules."""

    def __init__(self, db: Session):
        repository = CategoryRuleRepository(db)
        super().__init__(
            db=db,
            model=CategoryRule,
            repository=repository,
            read_schema=CategoryRuleRead
        )

    def get_active_by_type(self, transaction_type: str) -> List[CategoryRuleRead]:
        """Get all active rules for a transaction type."""
        try:
            enum_type = TransactionEnum(transaction_type)
        except ValueError:
            raise ValueError(f"Invalid transaction type: {transaction_type}")
        
        rules = self.repository.get_active_by_type(enum_type)
        return [self.read_schema.model_validate(r) for r in rules]

    def _get_category_model_by_type(self, transaction_type: str):
        try:
            enum_type = TransactionEnum(transaction_type)
        except ValueError:
            raise ValueError(f"Invalid transaction type: {transaction_type}")

        if enum_type == TransactionEnum.expense:
            from models import ExpensesCategory
            return ExpensesCategory
        elif enum_type == TransactionEnum.income:
            from models import IncomesCategory
            return IncomesCategory
        elif enum_type == TransactionEnum.investment:
            from models import InvestmentsCategory
            return InvestmentsCategory

        raise ValueError(f"Unsupported transaction type: {transaction_type}")

    def _category_exists_for_type(self, transaction_type: str, category_id: int) -> bool:
        if category_id is None:
            return False

        category_model = self._get_category_model_by_type(transaction_type)
        stmt = select(category_model).where(category_model.id == category_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def _validate_category_for_type(self, transaction_type: str, category_id: int) -> None:
        if category_id is None:
            raise ValueError("category_id is required")

        if not self._category_exists_for_type(transaction_type, category_id):
            raise ValueError(f"category_id {category_id} is invalid for type {transaction_type}")

    def create(self, data: CategoryRuleCreate) -> CategoryRuleRead:
        self._validate_category_for_type(data.type, data.category_id)
        return super().create(data)

    def update(self, id: int, data: CategoryRuleUpdate) -> Optional[CategoryRuleRead]:
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        update_data = data.model_dump(exclude_unset=True)
        type_to_check = update_data.get('type', getattr(existing.type, 'value', existing.type))
        category_id_to_check = update_data.get('category_id', existing.category_id)

        self._validate_category_for_type(type_to_check, category_id_to_check)

        return super().update(id, data)


class CategorizationService:
    """
    Service for categorizing transactions using rules + AI fallback.
    
    Flow:
    1. Get active rules for transaction type, ordered by priority DESC
    2. Apply regex match (case-insensitive) for each rule
    3. If match → return category_id
    4. If no match → call AI service (fallback is optional)
    5. If AI fails → return None (mark as needs_review)
    """

    def __init__(self, db: Session, ai_service=None):
        """
        Initialize categorization service.
        
        Args:
            db: SQLAlchemy session
            ai_service: Optional AI service for fallback categorization
        """
        self.db = db
        self.rule_repository = CategoryRuleRepository(db)
        self.ai_service = ai_service

    def categorize_transaction(
        self,
        description: str,
        transaction_type: str
    ) -> Optional[int]:
        """
        Categorize a transaction using rules + AI fallback.
        
        Args:
            description: Transaction description/name
            transaction_type: Type of transaction (expense|income|investment)
            
        Returns:
            category_id if match found, None otherwise
        """
        if not description or not transaction_type:
            return None

        try:
            enum_type = TransactionEnum(transaction_type)
        except ValueError:
            return None

        # Step 1: Get active rules ordered by priority DESC
        rules = self.rule_repository.get_active_by_type(enum_type)
        
        # Step 2: Apply regex matching
        for rule in rules:
            if rule.matches(description):
                return rule.category_id

        # Step 3: Fallback to AI service if available
        if self.ai_service:
            try:
                category_id = self.ai_service.categorize(description, transaction_type)
                if category_id:
                    return category_id
            except Exception as e:
                # Log error but don't crash
                print(f"AI categorization failed: {e}")

        # Step 4: Return None if no match and no AI
        return None

    def categorize_batch(
        self,
        transactions: List[dict]
    ) -> List[dict]:
        """
        Categorize multiple transactions in batch.
        
        Expected format:
        [
            {"description": "...", "type": "expense"},
            {...}
        ]
        
        Returns:
        [
            {"description": "...", "type": "expense", "category_id": 5 or None},
            {...}
        ]
        """
        result = []
        for transaction in transactions:
            category_id = self.categorize_transaction(
                description=transaction.get("description", ""),
                transaction_type=transaction.get("type", "")
            )
            transaction["category_id"] = category_id
            result.append(transaction)
        return result
