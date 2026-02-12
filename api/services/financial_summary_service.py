"""Service for FinancialSummary implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.financial_summary_repository import FinancialSummaryRepository
from schemas.financial_summary_schema import FinancialSummaryCreate, FinancialSummaryRead, FinancialSummaryUpdate
from models.models import FinancialSummary
from services.interfaces import ICRUDService


class FinancialSummaryService(ICRUDService[FinancialSummaryRead, FinancialSummaryCreate, FinancialSummaryUpdate]):
    """Service for FinancialSummary implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = FinancialSummaryRepository(db)

    def create(self, data: FinancialSummaryCreate) -> FinancialSummaryRead:
        obj = self.repository.create(**data.model_dump())
        return FinancialSummaryRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[FinancialSummaryRead]:
        obj = self.repository.get_by_id(id)
        return FinancialSummaryRead.model_validate(obj) if obj else None

    def get_all(self) -> List[FinancialSummaryRead]:
        return [FinancialSummaryRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: FinancialSummaryUpdate) -> Optional[FinancialSummaryRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return FinancialSummaryRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[FinancialSummaryRead]:
        return [FinancialSummaryRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
