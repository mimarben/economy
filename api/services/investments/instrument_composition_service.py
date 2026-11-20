"""Service for InstrumentComposition implementing CRUD operations."""
from typing import List
from sqlalchemy.orm import Session

from models import InstrumentComposition
from repositories.investments.instrument_composition_repository import InstrumentCompositionRepository
from schemas.investments.instrument_composition_schema import (
    InstrumentCompositionCreate, 
    InstrumentCompositionRead, 
    InstrumentCompositionUpdate
)
from services.core.base_service import BaseService


class InstrumentCompositionService(BaseService[InstrumentComposition, InstrumentCompositionRead, InstrumentCompositionCreate, InstrumentCompositionUpdate]):
    """Service for InstrumentComposition domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=InstrumentComposition,
            repository=InstrumentCompositionRepository(db),
            read_schema=InstrumentCompositionRead
        )

    def get_by_parent(self, parent_instrument_id: int) -> List[InstrumentCompositionRead]:
        """Get all compositions for a parent instrument."""
        objs = self.repository.get_composition_by_parent(parent_instrument_id)
        return [self.read_schema.model_validate(o) for o in objs]

    def get_by_child(self, child_instrument_id: int) -> List[InstrumentCompositionRead]:
        """Get all compositions where an instrument is a child."""
        objs = self.repository.get_composition_by_child(child_instrument_id)
        return [self.read_schema.model_validate(o) for o in objs]
