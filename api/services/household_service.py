"""Service for Household implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.household_repository import HouseholdRepository
from schemas.household_schema import HouseholdCreate, HouseholdRead, HouseholdUpdate
from models.models import Household
from services.interfaces import ICRUDService


class HouseholdService(ICRUDService[HouseholdRead, HouseholdCreate, HouseholdUpdate]):
    """Service for Household implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = HouseholdRepository(db)

    def create(self, data: HouseholdCreate) -> HouseholdRead:
        obj = self.repository.create(**data.model_dump())
        return HouseholdRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[HouseholdRead]:
        obj = self.repository.get_by_id(id)
        return HouseholdRead.model_validate(obj) if obj else None

    def get_all(self) -> List[HouseholdRead]:
        return [HouseholdRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: HouseholdUpdate) -> Optional[HouseholdRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return HouseholdRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[HouseholdRead]:
        return [HouseholdRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
