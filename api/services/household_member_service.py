"""Service for HouseholdMember implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.household_member_repository import HouseholdMemberRepository
from schemas.household_member_schema import HouseholdMemberCreate, HouseholdMemberRead, HouseholdMemberUpdate
from models.models import HouseholdMember
from services.interfaces import ICRUDService


class HouseholdMemberService(ICRUDService[HouseholdMemberRead, HouseholdMemberCreate, HouseholdMemberUpdate]):
    """Service for HouseholdMember implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = HouseholdMemberRepository(db)

    def create(self, data: HouseholdMemberCreate) -> HouseholdMemberRead:
        obj = self.repository.create(**data.model_dump())
        return HouseholdMemberRead.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[HouseholdMemberRead]:
        obj = self.repository.get_by_id(id)
        return HouseholdMemberRead.model_validate(obj) if obj else None

    def get_all(self) -> List[HouseholdMemberRead]:
        return [HouseholdMemberRead.model_validate(obj) for obj in self.repository.get_all()]

    def update(self, id: int, data: HouseholdMemberUpdate) -> Optional[HouseholdMemberRead]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return HouseholdMemberRead.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[HouseholdMemberRead]:
        return [HouseholdMemberRead.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
