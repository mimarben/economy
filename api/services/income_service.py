"""Service for Income implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.income_repository import IncomeRepository
from schemas.income_schema import IncomeCreate, IncomeRead, IncomeUpdate
from models.models import Income
from services.interfaces import ICRUDService


class IncomeService(ICRUDService[IncomeRead, IncomeCreate, IncomeUpdate]):
    """Service for Income implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = IncomeRepository(db)

    def create(self, data: IncomeCreate) -> IncomeRead:
        obj = self.repository.create(**data.model_dump())
        return IncomeRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[IncomeRead]:
        obj = self.repository.get_by_id(id)
        return IncomeRead.model_validate(obj) if obj else None

    def get_all(self) -> List[IncomeRead]:
        return [IncomeRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: IncomeUpdate) -> Optional[IncomeRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return IncomeRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[IncomeRead]:
        return [IncomeRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
