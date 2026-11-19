"""Service for market quotes: provider orchestration, quote cache and dashboard.

Business rules:
- Quotes are cached in market_quotes and refreshed only when older than
  MARKET_DATA_TTL_MINUTES (or on explicit force_refresh), so the external
  API is not hammered on every dashboard load.
- Providers are tried in order; the first one returning a quote wins. A
  failing provider degrades to stale cached data instead of an error.
"""
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Sequence

from sqlalchemy.orm import Session

from config import Config
from models import MarketQuote
from repositories.investments.investment_repository import InvestmentRepository
from repositories.investments.market_quote_repository import MarketQuoteRepository
from schemas.investments.market_quote_schema import (
    DashboardEntry,
    DashboardResponse,
    MarketQuoteOut,
)
from services.investments.market_provider import MarketDataProvider, ProviderQuote
from services.investments.yahoo_market_provider import YahooMarketProvider
from services.logs.logger_service import setup_logger

logger = setup_logger("market_quote_service")

STATUS_OK = "ok"
STATUS_STALE = "stale"
STATUS_UNAVAILABLE = "unavailable"


class MarketQuoteService:
    """Market quote cache and dashboard aggregation logic."""

    def __init__(self, db: Session, providers: Optional[Sequence[MarketDataProvider]] = None):
        self.db = db
        self.repository = MarketQuoteRepository(db)
        self.investment_repository = InvestmentRepository(db)
        self.providers: List[MarketDataProvider] = (
            list(providers) if providers is not None else [YahooMarketProvider()]
        )

    # ======================
    # QUOTES
    # ======================

    def get_quotes(self, isins: Sequence[str], force_refresh: bool = False) -> List[MarketQuoteOut]:
        """Quotes for the given ISINs, refreshing stale cache entries first."""
        normalized = _dedupe_preserving_order(isins)
        if not normalized:
            return []

        cached: Dict[str, MarketQuote] = {
            quote.isin: quote for quote in self.repository.get_by_isins(normalized)
        }
        now = datetime.utcnow()
        ttl = timedelta(minutes=Config.MARKET_DATA_TTL_MINUTES)

        stale_isins = [
            isin for isin in normalized
            if force_refresh
            or isin not in cached
            or cached[isin].fetched_at is None
            or (now - cached[isin].fetched_at) > ttl
        ]

        dirty = False
        for isin in stale_isins:
            known_symbol = cached[isin].symbol if isin in cached else None
            provider_quote = self._fetch_from_providers(isin, known_symbol)
            if provider_quote is None:
                logger.warning("No provider returned a quote for ISIN %s", isin)
                continue
            row = self.repository.upsert(MarketQuote(
                isin=provider_quote.isin,
                symbol=provider_quote.symbol,
                name=provider_quote.name,
                instrument_type=provider_quote.instrument_type,
                currency=provider_quote.currency,
                last_price=provider_quote.last_price,
                previous_close=provider_quote.previous_close,
                source=provider_quote.source,
                fetched_at=now,
            ))
            cached[isin] = row
            dirty = True

        if dirty:
            self.db.commit()

        return [self._to_out(cached.get(isin), isin) for isin in normalized]

    # ======================
    # DASHBOARD
    # ======================

    def get_dashboard(self, force_refresh: bool = False) -> DashboardResponse:
        """Portfolio grouped by ISIN joined with its market quote and position."""
        grouped = self.investment_repository.get_grouped_by_isin()
        positions = {
            row.isin: row
            for row in self.investment_repository.get_positions_by_isin()
        }
        quotes = {
            q.isin: q
            for q in self.get_quotes([row[0] for row in grouped], force_refresh=force_refresh)
        }

        entries: List[DashboardEntry] = []
        total = Decimal("0")
        total_market_value: Optional[Decimal] = None
        total_pl: Optional[Decimal] = None
        for isin, total_amount, contributions, last_date in grouped:
            total_amount = _to_decimal(total_amount) or Decimal("0")
            total += total_amount
            quote = quotes.get(isin)
            position = positions.get(isin)

            with_units = int(position.investments_with_units) if position is not None else 0
            # Never logged -> unknown position (None), NOT zero units
            units = (
                _to_decimal(position.units)
                if position is not None and with_units > 0 else None
            )
            reported_value = (
                _to_decimal(position.reported_value)
                if position is not None and with_units > 0 else None
            )

            market_value = _market_value(units, quote.last_price if quote else None)
            unrealized_pl = (
                (market_value - total_amount)
                if market_value is not None and units is not None else None
            )

            entry = DashboardEntry(
                isin=isin,
                name=quote.name if quote else None,
                symbol=quote.symbol if quote else None,
                instrument_type=quote.instrument_type if quote else None,
                currency=quote.currency if quote else None,
                total_contributed=total_amount,
                contributions=contributions,
                last_contribution_date=last_date,
                units=units,
                units_partial=0 < with_units < contributions,
                reported_value=reported_value,
                last_price=quote.last_price if quote else None,
                previous_close=quote.previous_close if quote else None,
                change_abs=quote.change_abs if quote else None,
                change_pct=quote.change_pct if quote else None,
                market_value=market_value,
                unrealized_pl=unrealized_pl,
                unrealized_pl_pct=_change_pct(unrealized_pl, total_amount),
                source=quote.source if quote else None,
                fetched_at=quote.fetched_at if quote else None,
                quote_status=quote.status if quote else STATUS_UNAVAILABLE,
            )
            entries.append(entry)

            if entry.market_value is not None:
                total_market_value = (total_market_value or Decimal("0")) + entry.market_value
            if entry.unrealized_pl is not None:
                total_pl = (total_pl or Decimal("0")) + entry.unrealized_pl

        without_count, without_amount = self.investment_repository.get_totals_without_isin()
        return DashboardResponse(
            entries=entries,
            without_isin_count=without_count,
            without_isin_amount=_to_decimal(without_amount) or Decimal("0"),
            total_contributed=total,
            total_market_value=total_market_value,
            total_unrealized_pl=total_pl,
            generated_at=datetime.utcnow(),
        )

    # ======================
    # INTERNALS
    # ======================

    def _fetch_from_providers(self, isin: str, known_symbol: Optional[str] = None) -> Optional[ProviderQuote]:
        for provider in self.providers:
            try:
                quote = provider.fetch_quote(isin, known_symbol=known_symbol)
            except Exception as error:  # providers contract: never raise, but be safe
                logger.warning("Provider %s raised for %s: %s", provider.source_name, isin, error)
                continue
            if quote is not None:
                return quote
        return None

    def _to_out(self, row: Optional[MarketQuote], isin: str) -> MarketQuoteOut:
        if row is None:
            return MarketQuoteOut(isin=isin, status=STATUS_UNAVAILABLE)

        status = STATUS_OK
        fetched_at = row.fetched_at
        if fetched_at is not None:
            age = datetime.utcnow() - fetched_at
            if age > timedelta(minutes=Config.MARKET_DATA_TTL_MINUTES):
                status = STATUS_STALE

        change_abs = _change_abs(row.last_price, row.previous_close)
        return MarketQuoteOut(
            isin=isin,
            symbol=row.symbol,
            name=row.name,
            instrument_type=row.instrument_type,
            currency=row.currency,
            last_price=row.last_price,
            previous_close=row.previous_close,
            change_abs=change_abs,
            change_pct=_change_pct(change_abs, row.previous_close),
            source=row.source,
            fetched_at=fetched_at,
            status=status,
        )


def _dedupe_preserving_order(isins: Sequence[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for isin in isins:
        normalized = isin.strip().upper() if isinstance(isin, str) else isin
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def _to_decimal(value) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _market_value(units: Optional[Decimal], last_price: Optional[Decimal]) -> Optional[Decimal]:
    if units is None or last_price is None:
        return None
    return (units * last_price).quantize(Decimal("0.01"))


def _change_abs(last: Optional[Decimal], previous: Optional[Decimal]) -> Optional[Decimal]:
    if last is None or previous is None:
        return None
    return (last - previous).quantize(Decimal("0.0001"))


def _change_pct(change_abs: Optional[Decimal], previous: Optional[Decimal]) -> Optional[Decimal]:
    if change_abs is None or previous is None or previous == 0:
        return None
    return ((change_abs / previous) * 100).quantize(Decimal("0.01"))
