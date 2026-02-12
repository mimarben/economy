"""Repository for ExpensesCategory entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models.models import ExpensesCategory


class ExpensesCategoryRepository(BaseRepository[ExpensesCategory]):
    """Repository for ExpensesCategory with custom queries."""

    def __init__(self, db):
        super().__init__(db, ExpensesCategory)
