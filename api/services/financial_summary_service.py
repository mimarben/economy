"""Service for FinancialSummary implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.financial_summary_repository import FinancialSummaryRepository
from schemas.financial_summary_schema import FinancialSummaryCreate, FinancialSummaryRead, FinancialSummaryUpdate
from models.models import FinancialSummary
from services.base_service import BaseService


class FinancialSummaryService(BaseService[FinancialSummary, FinancialSummaryRead, FinancialSummaryCreate, FinancialSummaryUpdate]):
    """Service for FinancialSummary domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=FinancialSummary,
            repository=FinancialSummaryRepository(db),
            read_schema=FinancialSummaryRead
        )
