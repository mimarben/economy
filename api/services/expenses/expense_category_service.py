"""Service for ExpensesCategory implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.expenses.expense_category_repository import ExpensesCategoryRepository
from schemas.expenses.expense_category_schema import ExpenseCategoryCreate, ExpenseCategoryRead, ExpenseCategoryUpdate
from models import ExpensesCategory
from services.core.base_service import BaseService


class ExpensesCategoryService(BaseService[ExpensesCategory, ExpenseCategoryRead, ExpenseCategoryCreate, ExpenseCategoryUpdate]):
    """Service for ExpensesCategory domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=ExpensesCategory,
            repository=ExpensesCategoryRepository(db),
            read_schema=ExpenseCategoryRead
        )
