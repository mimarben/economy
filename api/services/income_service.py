"""Service for Income implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.income_repository import IncomeRepository
from schemas.income_schema import IncomeCreate, IncomeRead, IncomeUpdate
from models.models import Income
from services.base_service import BaseService


class IncomeService(BaseService[Income, IncomeRead, IncomeCreate, IncomeUpdate]):
    """Service for Income domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Income,
            repository=IncomeRepository(db),
            read_schema=IncomeRead
        )
