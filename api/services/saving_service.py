"""Service for Saving implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.saving_repository import SavingRepository
from schemas.saving_schema import SavingCreate, SavingRead, SavingUpdate
from models.models import Saving
from services.interfaces import ICRUDService


class SavingService(ICRUDService[SavingRead, SavingCreate, SavingUpdate]):
    """Service for Saving implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = SavingRepository(db)

    def create(self, data: SavingCreate) -> SavingRead:
        obj = self.repository.create(**data.model_dump())
        return SavingRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[SavingRead]:
        obj = self.repository.get_by_id(id)
        return SavingRead.model_validate(obj) if obj else None

    def get_all(self) -> List[SavingRead]:
        return [SavingRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: SavingUpdate) -> Optional[SavingRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return SavingRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[SavingRead]:
        return [SavingRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
