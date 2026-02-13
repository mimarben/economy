"""Service for InvestmentLog implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.investment_log_repository import InvestmentLogRepository
from schemas.investment_log_schema import InvestmentLogCreate, InvestmentLogRead, InvestmentLogUpdate
from models import InvestmentLog
from services.base_service import BaseService


class InvestmentLogService(BaseService[InvestmentLog, InvestmentLogRead, InvestmentLogCreate, InvestmentLogUpdate]):
    """Service for InvestmentLog domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=InvestmentLog,
            repository=InvestmentLogRepository(db),
            read_schema=InvestmentLogRead
        )
