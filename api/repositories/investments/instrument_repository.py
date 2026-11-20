"""Repository for Instrument entity following segregated interfaces."""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import aliased

from models import Instrument, InstrumentIdentifier, Investment
from repositories.core.base_repository import BaseRepository


class InstrumentRepository(BaseRepository[Instrument]):
    """Repository for Instrument with custom queries."""

    def __init__(self, db):
        super().__init__(db, Instrument)

    def search_by_isin(self, isin: str) -> List[Instrument]:
        """Search instruments by ISIN identifier."""
        stmt = self._base_query()
        stmt = stmt.join(InstrumentIdentifier).where(
            InstrumentIdentifier.identifier_type == "ISIN",
            InstrumentIdentifier.value == isin
        )
        return self.db.execute(stmt).scalars().all()

    def search_by_name(self, name: str) -> List[Instrument]:
        """Search instruments by name (partial match)."""
        stmt = self._base_query()
        stmt = stmt.where(Instrument.name.ilike(f"%{name}%"))
        return self.db.execute(stmt).scalars().all()

    def search_by_ticker(self, ticker: str) -> List[Instrument]:
        """Search instruments by ticker identifier."""
        stmt = self._base_query()
        stmt = stmt.join(InstrumentIdentifier).where(
            InstrumentIdentifier.identifier_type == "TICKER",
            InstrumentIdentifier.value == ticker
        )
        return self.db.execute(stmt).scalars().all()

    def search_by_provider_identifier(self, provider: str, identifier: str) -> List[Instrument]:
        """Search instruments by provider identifier."""
        stmt = self._base_query()
        stmt = stmt.join(InstrumentIdentifier).where(
            InstrumentIdentifier.identifier_type == "PROVIDER",
            InstrumentIdentifier.provider == provider,
            InstrumentIdentifier.value == identifier
        )
        return self.db.execute(stmt).scalars().all()

    def attach_investment(self, instrument_id: int, investment_id: int) -> bool:
        """Attach an existing investment to an instrument."""
        investment = self.db.execute(
            select(Investment).where(
                Investment.id == investment_id,
                Investment.deleted_at.is_(None)
            )
        ).scalars().one_or_none()
        
        if investment is None:
            return False
        
        investment.instrument_id = instrument_id
        self.db.flush()
        return True

    def get_by_isin(self, isin: str) -> Optional[Instrument]:
        """Get instrument by ISIN identifier."""
        stmt = self._base_query()
        stmt = stmt.join(InstrumentIdentifier).where(
            InstrumentIdentifier.identifier_type == "ISIN",
            InstrumentIdentifier.value == isin
        )
        return self.db.execute(stmt).scalars().one_or_none()

    def get_by_ticker(self, ticker: str) -> Optional[Instrument]:
        """Get instrument by ticker identifier."""
        stmt = self._base_query()
        stmt = stmt.join(InstrumentIdentifier).where(
            InstrumentIdentifier.identifier_type == "TICKER",
            InstrumentIdentifier.value == ticker
        )
        return self.db.execute(stmt).scalars().one_or_none()

    def get_by_provider_identifier(self, provider: str, identifier: str) -> Optional[Instrument]:
        """Get instrument by provider identifier."""
        stmt = self._base_query()
        stmt = stmt.join(InstrumentIdentifier).where(
            InstrumentIdentifier.identifier_type == "PROVIDER",
            InstrumentIdentifier.provider == provider,
            InstrumentIdentifier.value == identifier
        )
        return self.db.execute(stmt).scalars().one_or_none()
