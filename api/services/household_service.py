"""Service for Household implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.household_repository import HouseholdRepository
from schemas.household_schema import HouseholdCreate, HouseholdRead, HouseholdUpdate
from models.models import Household
from services.base_service import BaseService


class HouseholdService(BaseService[Household, HouseholdRead, HouseholdCreate, HouseholdUpdate]):
    """Service for Household domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Household,
            repository=HouseholdRepository(db),
            read_schema=HouseholdRead
        )
