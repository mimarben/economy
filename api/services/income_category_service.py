"""Service for IncomesCategory implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.income_category_repository import IncomesCategoryRepository
from schemas.income_category_schema import IncomeCategoryCreate, IncomeCategoryRead, IncomeCategoryUpdate
from models.models import IncomesCategory
from services.interfaces import ICRUDService


class IncomesCategoryService(ICRUDService[IncomeCategoryRead, IncomeCategoryCreate, IncomeCategoryUpdate]):
    """Service for IncomesCategory implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = IncomesCategoryRepository(db)

    def create(self, data: IncomeCategoryCreate) -> IncomeCategoryRead:
        obj = self.repository.create(**data.model_dump())
        return IncomeCategoryRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[IncomeCategoryRead]:
        obj = self.repository.get_by_id(id)
        return IncomeCategoryRead.model_validate(obj) if obj else None

    def get_all(self) -> List[IncomeCategoryRead]:
        return [IncomeCategoryRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: IncomeCategoryUpdate) -> Optional[IncomeCategoryRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return IncomeCategoryRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[IncomeCategoryRead]:
        return [IncomeCategoryRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
