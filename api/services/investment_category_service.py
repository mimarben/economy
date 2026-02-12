"""Service for InvestmentsCategory implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.investment_category_repository import InvestmentsCategoryRepository
from schemas.investment_category_schema import InvestmentCategoryCreate, InvestmentCategoryRead, InvestmentCategoryUpdate
from models.models import InvestmentsCategory
from services.interfaces import ICRUDService


class InvestmentsCategoryService(ICRUDService[InvestmentCategoryRead, InvestmentCategoryCreate, InvestmentCategoryUpdate]):
    """Service for InvestmentsCategory implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = InvestmentsCategoryRepository(db)

    def create(self, data: InvestmentCategoryCreate) -> InvestmentCategoryRead:
        obj = self.repository.create(**data.model_dump())
        return InvestmentCategoryRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[InvestmentCategoryRead]:
        obj = self.repository.get_by_id(id)
        return InvestmentCategoryRead.model_validate(obj) if obj else None

    def get_all(self) -> List[InvestmentCategoryRead]:
        return [InvestmentCategoryRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: InvestmentCategoryUpdate) -> Optional[InvestmentCategoryRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return InvestmentCategoryRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[InvestmentCategoryRead]:
        return [InvestmentCategoryRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
