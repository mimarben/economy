"""Service for SavingLog implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.saving_log_repository import SavingLogRepository
from schemas.saving_log_schema import SavingLogCreate, SavingLogRead, SavingLogUpdate
from models.models import SavingLog
from services.interfaces import ICRUDService


class SavingLogService(ICRUDService[SavingLogRead, SavingLogCreate, SavingLogUpdate]):
    """Service for SavingLog implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = SavingLogRepository(db)

    def create(self, data: SavingLogCreate) -> SavingLogRead:
        obj = self.repository.create(**data.model_dump())
        return SavingLogRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[SavingLogRead]:
        obj = self.repository.get_by_id(id)
        return SavingLogRead.model_validate(obj) if obj else None

    def get_all(self) -> List[SavingLogRead]:
        return [SavingLogRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: SavingLogUpdate) -> Optional[SavingLogRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return SavingLogRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[SavingLogRead]:
        return [SavingLogRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
