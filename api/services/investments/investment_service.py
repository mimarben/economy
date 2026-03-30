"""Service for Investment implementing CRUD operations."""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from repositories.investments.investment_repository import InvestmentRepository
from schemas.investments.investment_schema import InvestmentCreate, InvestmentRead, InvestmentUpdate
from models import Investment
from services.core.base_service import BaseService
from services.core.dedup_service import generate_dedup_hash


class InvestmentService(BaseService[Investment, InvestmentRead, InvestmentCreate, InvestmentUpdate]):
    """Service for Investment domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Investment,
            repository=InvestmentRepository(db),
            read_schema=InvestmentRead
        )

    def create(self, data: InvestmentCreate) -> InvestmentRead:
        dedup_hash = generate_dedup_hash(
            account_id=data.account_id,
            txn_date=data.date,
            amount=data.amount,
            description=data.description,
        )

        obj = Investment(**data.model_dump(), dedup_hash=dedup_hash)

        try:
            obj = self.repository.create(obj)
        except IntegrityError as e:
            if 'uq_investments_account_dedup_hash' in str(e.orig):
                raise ValueError("DUPLICATE_TRANSACTION")
            raise

        return InvestmentRead.model_validate(obj)

