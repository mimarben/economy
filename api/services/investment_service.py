"""Service for Investment implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.investment_repository import InvestmentRepository
from schemas.investment_schema import InvestmentCreate, InvestmentRead, InvestmentUpdate
from models.models import Investment
from services.interfaces import ICRUDService


class InvestmentService(ICRUDService[InvestmentRead, InvestmentCreate, InvestmentUpdate]):
    """Service for Investment implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = InvestmentRepository(db)

    def create(self, data: InvestmentCreate) -> InvestmentRead:
        obj = self.repository.create(**data.model_dump())
        return InvestmentRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[InvestmentRead]:
        obj = self.repository.get_by_id(id)
        return InvestmentRead.model_validate(obj) if obj else None

    def get_all(self) -> List[InvestmentRead]:
        return [InvestmentRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: InvestmentUpdate) -> Optional[InvestmentRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return InvestmentRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[InvestmentRead]:
        return [InvestmentRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
