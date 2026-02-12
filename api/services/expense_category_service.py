"""Service for ExpensesCategory implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.expense_category_repository import ExpensesCategoryRepository
from schemas.expense_category_schema import ExpenseCategoryCreate, ExpenseCategoryRead, ExpenseCategoryUpdate
from models.models import ExpensesCategory
from services.interfaces import ICRUDService


class ExpensesCategoryService(ICRUDService[ExpenseCategoryRead, ExpenseCategoryCreate, ExpenseCategoryUpdate]):
    """Service for ExpensesCategory implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ExpensesCategoryRepository(db)

    def create(self, data: ExpenseCategoryCreate) -> ExpenseCategoryRead:
        obj = self.repository.create(**data.model_dump())
        return ExpenseCategoryRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[ExpenseCategoryRead]:
        obj = self.repository.get_by_id(id)
        return ExpenseCategoryRead.model_validate(obj) if obj else None

    def get_all(self) -> List[ExpenseCategoryRead]:
        return [ExpenseCategoryRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: ExpenseCategoryUpdate) -> Optional[ExpenseCategoryRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return ExpenseCategoryRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[ExpenseCategoryRead]:
        return [ExpenseCategoryRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
