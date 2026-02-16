"""Service for Household implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.households.household_repository import HouseholdRepository
from schemas.households.household_schema import HouseholdCreate, HouseholdRead, HouseholdUpdate
from models import Household
from services.core.base_service import BaseService


class HouseholdService(BaseService[Household, HouseholdRead, HouseholdCreate, HouseholdUpdate]):
    """Service for Household domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Household,
            repository=HouseholdRepository(db),
            read_schema=HouseholdRead
        )
