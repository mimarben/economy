"""Service for IncomesCategory implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.income_category_repository import IncomesCategoryRepository
from schemas.income_category_schema import IncomeCategoryCreate, IncomeCategoryRead, IncomeCategoryUpdate
from models import IncomesCategory
from services.base_service import BaseService


class IncomesCategoryService(BaseService[IncomesCategory, IncomeCategoryRead, IncomeCategoryCreate, IncomeCategoryUpdate]):
    """Service for IncomesCategory domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=IncomesCategory,
            repository=IncomesCategoryRepository(db),
            read_schema=IncomeCategoryRead
        )
