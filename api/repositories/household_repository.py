"""Repository for Household entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models import Household


class HouseholdRepository(BaseRepository[Household]):
    """Repository for Household with custom queries."""

    def __init__(self, db):
        super().__init__(db, Household)
