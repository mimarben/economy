"""Repository for InstrumentComposition entity."""
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models import InstrumentComposition, Instrument
from repositories.core.base_repository import BaseRepository


class InstrumentCompositionRepository(BaseRepository[InstrumentComposition]):
    """Repository for InstrumentComposition with CRUD operations."""

    def __init__(self, db: Session):
        super().__init__(db, InstrumentComposition)

    def get_composition_by_parent(self, parent_instrument_id: int) -> List[InstrumentComposition]:
        """Get all compositions for a parent instrument."""
        stmt = self._base_query().where(
            InstrumentComposition.parent_instrument_id == parent_instrument_id
        )
        return self.db.execute(stmt).scalars().all()

    def get_composition_by_child(self, child_instrument_id: int) -> List[InstrumentComposition]:
        """Get all compositions where an instrument is a child."""
        stmt = self._base_query().where(
            InstrumentComposition.child_instrument_id == child_instrument_id
        )
        return self.db.execute(stmt).scalars().all()

    def get_parent_instruments(self, child_instrument_id: int) -> List[Instrument]:
        """Get all parent instruments for a child instrument."""
        stmt = (
            select(Instrument)
            .join(InstrumentComposition, Instrument.id == InstrumentComposition.parent_instrument_id)
            .where(
                InstrumentComposition.child_instrument_id == child_instrument_id,
                Instrument.deleted_at.is_(None)
            )
        )
        return self.db.execute(stmt).scalars().all()

    def get_child_instruments(self, parent_instrument_id: int) -> List[Instrument]:
        """Get all child instruments for a parent instrument."""
        stmt = (
            select(Instrument)
            .join(InstrumentComposition, Instrument.id == InstrumentComposition.child_instrument_id)
            .where(
                InstrumentComposition.parent_instrument_id == parent_instrument_id,
                Instrument.deleted_at.is_(None)
            )
        )
        return self.db.execute(stmt).scalars().all()

    def get_total_weight(self, parent_instrument_id: int) -> Optional[float]:
        """Get the sum of weights for a parent instrument composition."""
        stmt = (
            select(func.sum(InstrumentComposition.weight))
            .where(
                InstrumentComposition.parent_instrument_id == parent_instrument_id,
                InstrumentComposition.deleted_at.is_(None)
            )
        )
        result = self.db.execute(stmt).scalar()
        return float(result) if result else None
