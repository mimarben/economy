"""Repository for HouseholdMember entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models.models import HouseholdMember


class HouseholdMemberRepository(BaseRepository[HouseholdMember]):
    """Repository for HouseholdMember with custom queries."""

    def __init__(self, db):
        super().__init__(db, HouseholdMember)
