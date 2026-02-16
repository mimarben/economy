"""Service for InvestmentsCategory implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.investments.investment_category_repository import InvestmentsCategoryRepository
from schemas.investments.investment_category_schema import InvestmentCategoryCreate, InvestmentCategoryRead, InvestmentCategoryUpdate
from models import InvestmentsCategory
from services.core.base_service import BaseService


class InvestmentsCategoryService(BaseService[InvestmentsCategory, InvestmentCategoryRead, InvestmentCategoryCreate, InvestmentCategoryUpdate]):
    """Service for InvestmentsCategory domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=InvestmentsCategory,
            repository=InvestmentsCategoryRepository(db),
            read_schema=InvestmentCategoryRead
        )
