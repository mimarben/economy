"""Service for Investment implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.investment_repository import InvestmentRepository
from schemas.investment_schema import InvestmentCreate, InvestmentRead, InvestmentUpdate
from models import Investment
from services.base_service import BaseService


class InvestmentService(BaseService[Investment, InvestmentRead, InvestmentCreate, InvestmentUpdate]):
    """Service for Investment domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Investment,
            repository=InvestmentRepository(db),
            read_schema=InvestmentRead
        )
