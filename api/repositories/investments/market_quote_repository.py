"""Repository for MarketQuote entity (quote cache)."""
from datetime import datetime
from typing import Iterable, List, Optional

from sqlalchemy import select

from repositories.core.base_repository import BaseRepository
from models import MarketQuote, MarketQuoteHistory, Instrument
from models.investments import InstrumentIdentifier, IdentifierTypeEnum


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
        """Insert or update the cached row for quote.isin (flush only).

        Also appends to market_quote_history for historical tracking.
        """
        existing = self.get_by_isin(quote.isin)
        if existing is None:
            existing = self.create(quote)
        else:
            existing.symbol = quote.symbol
            existing.name = quote.name
            existing.instrument_type = quote.instrument_type
            existing.currency = quote.currency
            existing.last_price = quote.last_price
            existing.previous_close = quote.previous_close
            existing.source = quote.source
            existing.fetched_at = quote.fetched_at
            existing.quoted_at = quote.quoted_at
            existing.price_type = quote.price_type
            self.db.flush()

        # Always append to history (append-only, no upsert)
        self._append_history(existing)

        return existing

    def _append_history(self, quote: MarketQuote) -> None:
        """Append quote to history table (append-only)."""
        # Check if we already have a history entry for this instrument + quoted_at + source
        # to avoid duplicates when providers return the same quote multiple times
        if quote.instrument_id is None:
            # Try to find or create instrument for ISIN
            instrument = self._get_or_create_instrument(quote)
            if instrument:
                quote.instrument_id = instrument.id

        if quote.instrument_id is None:
            return

        # Check for duplicate history entry
        stmt = select(MarketQuoteHistory).where(
            MarketQuoteHistory.instrument_id == quote.instrument_id,
            MarketQuoteHistory.price == quote.last_price,
            MarketQuoteHistory.quoted_at == quote.quoted_at,
            MarketQuoteHistory.source == quote.source,
        )
        existing = self.db.execute(stmt).scalars().one_or_none()
        if existing:
            return

        history = MarketQuoteHistory(
            instrument_id=quote.instrument_id,
            price=quote.last_price,
            quoted_at=quote.quoted_at or datetime.utcnow(),
            price_type=quote.price_type,
            source=quote.source,
        )
        self.db.add(history)
        self.db.flush()

    def _get_or_create_instrument(self, quote: MarketQuote) -> Optional[Instrument]:
        """Get or create instrument from ISIN for legacy quotes."""
        # Try to find instrument by ISIN identifier
        stmt = select(Instrument).join(InstrumentIdentifier).where(
            InstrumentIdentifier.identifier_type == IdentifierTypeEnum.ISIN,
            InstrumentIdentifier.value == quote.isin,
        )
        instrument = self.db.execute(stmt).scalars().one_or_none()
        if instrument:
            return instrument

        # Create new instrument if not found (for backward compatibility)
        instrument = Instrument(
            name=quote.name or quote.isin,
            asset_class=self._infer_asset_class(quote.instrument_type),
            category_id=1,  # Default to "OTHER" category - should be seeded
            currency=quote.currency or "EUR",
            instrument_type=quote.instrument_type,
        )
        self.db.add(instrument)
        self.db.flush()

        # Add ISIN identifier
        identifier = InstrumentIdentifier(
            instrument_id=instrument.id,
            identifier_type=IdentifierTypeEnum.ISIN,
            value=quote.isin,
            is_primary=True,
        )
        self.db.add(identifier)
        self.db.flush()

        return instrument

    def _infer_asset_class(self, instrument_type: Optional[str]) -> str:
        """Infer asset class from instrument type string."""
        if not instrument_type:
            return "OTHER"

        type_lower = instrument_type.lower()
        if "etf" in type_lower:
            return "ETF"
        elif "fund" in type_lower or "mutual" in type_lower:
            return "FUND"
        elif "stock" in type_lower or "equity" in type_lower:
            return "STOCK"
        elif "crypto" in type_lower or type_lower in ("btc", "eth"):
            return "CRYPTO"
        elif "bond" in type_lower:
            return "BOND"
        elif "index" in type_lower:
            return "OTHER"
        return "OTHER"
