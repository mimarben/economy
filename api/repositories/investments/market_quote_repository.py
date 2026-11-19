"""Repository for MarketQuote entity (quote cache)."""
from typing import Iterable, List, Optional

from sqlalchemy import select

from repositories.core.base_repository import BaseRepository
from models import MarketQuote


class MarketQuoteRepository(BaseRepository[MarketQuote]):
    """Repository for MarketQuote with cache-oriented queries."""

    def __init__(self, db):
        super().__init__(db, MarketQuote)

    def get_by_isin(self, isin: str) -> Optional[MarketQuote]:
        stmt = self._base_query().where(MarketQuote.isin == isin)
        return self.db.execute(stmt).scalars().one_or_none()

    def get_by_isins(self, isins: Iterable[str]) -> List[MarketQuote]:
        isin_list = list(isins)
        if not isin_list:
            return []
        stmt = self._base_query().where(MarketQuote.isin.in_(isin_list))
        return self.db.execute(stmt).scalars().all()

    def upsert(self, quote: MarketQuote) -> MarketQuote:
        """Insert or update the cached row for quote.isin (flush only)."""
        existing = self.get_by_isin(quote.isin)
        if existing is None:
            return self.create(quote)

        existing.symbol = quote.symbol
        existing.name = quote.name
        existing.instrument_type = quote.instrument_type
        existing.currency = quote.currency
        existing.last_price = quote.last_price
        existing.previous_close = quote.previous_close
        existing.source = quote.source
        existing.fetched_at = quote.fetched_at
        self.db.flush()
        return existing
