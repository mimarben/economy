"""Service for Instrument implementing CRUD operations."""
from typing import List, Optional
from sqlalchemy.orm import Session

from models import Instrument
from repositories.investments.instrument_repository import InstrumentRepository
from schemas.investments.instrument_schema import InstrumentCreate, InstrumentRead, InstrumentUpdate
from services.core.base_service import BaseService


class InstrumentService(BaseService[Instrument, InstrumentRead, InstrumentCreate, InstrumentUpdate]):
    """Service for Instrument domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Instrument,
            repository=InstrumentRepository(db),
            read_schema=InstrumentRead
        )

    def search_by_isin(self, isin: str) -> List[InstrumentRead]:
        """Search instruments by ISIN identifier."""
        objs = self.repository.search_by_isin(isin)
        return [self.read_schema.model_validate(o) for o in objs]

    def search_by_name(self, name: str) -> List[InstrumentRead]:
        """Search instruments by name (partial match)."""
        objs = self.repository.search_by_name(name)
        return [self.read_schema.model_validate(o) for o in objs]

    def search_by_ticker(self, ticker: str) -> List[InstrumentRead]:
        """Search instruments by ticker identifier."""
        objs = self.repository.search_by_ticker(ticker)
        return [self.read_schema.model_validate(o) for o in objs]

    def search_by_provider_identifier(self, provider: str, identifier: str) -> List[InstrumentRead]:
        """Search instruments by provider identifier."""
        objs = self.repository.search_by_provider_identifier(provider, identifier)
        return [self.read_schema.model_validate(o) for o in objs]

    def attach_investment(self, instrument_id: int, investment_id: int) -> Optional[InstrumentRead]:
        """Attach an existing investment to an instrument."""
        success = self.repository.attach_investment(instrument_id, investment_id)
        if success:
            self.db.commit()
            obj = self.repository.get_by_id(instrument_id)
            return self.read_schema.model_validate(obj) if obj else None
        return None
