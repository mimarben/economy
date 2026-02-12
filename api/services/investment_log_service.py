"""Service for InvestmentLog implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.investment_log_repository import InvestmentLogRepository
from schemas.investment_log_schema import InvestmentLogCreate, InvestmentLogRead, InvestmentLogUpdate
from models.models import InvestmentLog
from services.interfaces import ICRUDService


class InvestmentLogService(ICRUDService[InvestmentLogRead, InvestmentLogCreate, InvestmentLogUpdate]):
    """Service for InvestmentLog implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = InvestmentLogRepository(db)

    def create(self, data: InvestmentLogCreate) -> InvestmentLogRead:
        obj = self.repository.create(**data.model_dump())
        return InvestmentLogRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[InvestmentLogRead]:
        obj = self.repository.get_by_id(id)
        return InvestmentLogRead.model_validate(obj) if obj else None

    def get_all(self) -> List[InvestmentLogRead]:
        return [InvestmentLogRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: InvestmentLogUpdate) -> Optional[InvestmentLogRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return InvestmentLogRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[InvestmentLogRead]:
        return [InvestmentLogRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
