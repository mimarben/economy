"""Service for HouseholdMember implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.households.household_member_repository import HouseholdMemberRepository
from schemas.households.household_member_schema import HouseholdMemberCreate, HouseholdMemberRead, HouseholdMemberUpdate
from models import HouseholdMember
from services.core.base_service import BaseService


class HouseholdMemberService(BaseService[HouseholdMember, HouseholdMemberRead, HouseholdMemberCreate, HouseholdMemberUpdate]):
    """Service for HouseholdMember domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=HouseholdMember,
            repository=HouseholdMemberRepository(db),
            read_schema=HouseholdMemberRead
        )
