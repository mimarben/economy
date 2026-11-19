"""MarketQuoteService: cache TTL, provider fallback and dashboard grouping.

All tests run against the in-memory SQLite session from conftest and a
fake provider, so no network access is involved.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from models import Investment, InvestmentLog, MarketQuote
from services.investments.market_provider import MarketDataProvider, ProviderQuote
from services.investments.market_quote_service import MarketQuoteService

ISIN_A = "IE00B83YJG36"   # iShares Developed Real Estate
ISIN_B = "LU0996175948"   # Amundi Index MSCI Emerging Markets
ISIN_C = "IE0032126645"   # Vanguard U.S. 500


class FakeProvider(MarketDataProvider):
    """Scripted provider: returns canned quotes and counts calls."""

    def __init__(self, quotes: dict[str, ProviderQuote | None]):
        self.quotes = quotes
        self.calls: list[str] = []

    @property
    def source_name(self) -> str:
        return "fake"

    def fetch_quote(self, isin: str, known_symbol: str | None = None):
        self.calls.append(isin)
        return self.quotes.get(isin)


def _quote(isin: str, last: str = "110.0", prev: str = "100.0") -> ProviderQuote:
    return ProviderQuote(
        isin=isin,
        symbol=f"SYM-{isin[:4]}",
        name=f"Fund {isin}",
        instrument_type="MUTUALFUND",
        currency="EUR",
        last_price=Decimal(last),
        previous_close=Decimal(prev),
        source="fake",
    )


def _service(db_session, quotes: dict | None = None) -> tuple[MarketQuoteService, FakeProvider]:
    provider = FakeProvider(quotes or {})
    return MarketQuoteService(db_session, providers=[provider]), provider


def _investment(db_session, isin: str | None, amount: str, when: date) -> Investment:
    investment = Investment(
        description=f"contribution {isin or 'cash'} {when}",
        date=when,
        currency="EUR",
        amount=Decimal(amount),
        dedup_hash=f"hash-{isin}-{when}-{amount}",
        isin=isin,
        account_id=1,
        category_id=1,
    )
    db_session.add(investment)
    db_session.commit()
    return investment


def _log(
    db_session,
    investment: Investment,
    when: date,
    quantity: str,
    current_value: str | None = None,
    price_per_unit: str | None = None,
) -> None:
    """Position snapshot log; the latest one per investment wins."""
    db_session.add(InvestmentLog(
        investment_id=investment.id,
        date=when,
        current_value=Decimal(current_value) if current_value else None,
        price_per_unit=Decimal(price_per_unit) if price_per_unit else None,
        quantity=Decimal(quantity),
        action="HOLD",
    ))
    db_session.commit()


class TestGetQuotesCache:
    def test_first_call_fetches_and_caches(self, db_session):
        service, provider = _service(db_session, {ISIN_A: _quote(ISIN_A)})

        quotes = service.get_quotes([ISIN_A])

        assert provider.calls == [ISIN_A]
        assert quotes[0].isin == ISIN_A
        assert quotes[0].last_price == Decimal("110.0")
        assert quotes[0].change_abs == Decimal("10.0000")
        assert quotes[0].change_pct == Decimal("10.00")
        assert quotes[0].status == "ok"

        stored = db_session.execute(select(MarketQuote)).scalars().all()
        assert len(stored) == 1
        assert stored[0].isin == ISIN_A
        assert stored[0].source == "fake"

    def test_second_call_within_ttl_uses_cache(self, db_session):
        service, provider = _service(db_session, {ISIN_A: _quote(ISIN_A)})
        service.get_quotes([ISIN_A])
        provider.calls.clear()

        service.get_quotes([ISIN_A])

        assert provider.calls == [], "fresh cache must not hit the provider"

    def test_force_refresh_bypasses_cache(self, db_session):
        service, provider = _service(db_session, {ISIN_A: _quote(ISIN_A)})
        service.get_quotes([ISIN_A])
        provider.calls.clear()

        service.get_quotes([ISIN_A], force_refresh=True)

        assert provider.calls == [ISIN_A]

    def test_expired_cache_is_refetched(self, db_session):
        service, provider = _service(db_session, {ISIN_A: _quote(ISIN_A)})
        service.get_quotes([ISIN_A])
        provider.calls.clear()
        # Age the cached row beyond the TTL
        row = service.repository.get_by_isin(ISIN_A)
        row.fetched_at = datetime.utcnow() - timedelta(hours=2)
        db_session.commit()

        service.get_quotes([ISIN_A])

        assert provider.calls == [ISIN_A]

    def test_isin_normalized_and_deduplicated(self, db_session):
        service, provider = _service(db_session, {ISIN_A: _quote(ISIN_A)})

        quotes = service.get_quotes([ISIN_A.lower(), ISIN_A, f" {ISIN_B} "])

        assert [q.isin for q in quotes] == [ISIN_A, ISIN_B]
        assert provider.calls == [ISIN_A, ISIN_B]

    def test_provider_failure_reports_unavailable(self, db_session):
        service, provider = _service(db_session, {})  # nothing resolvable

        quotes = service.get_quotes([ISIN_A])

        assert quotes[0].status == "unavailable"
        assert quotes[0].last_price is None

    def test_provider_failure_keeps_stale_cache(self, db_session):
        service, provider = _service(db_session, {ISIN_A: _quote(ISIN_A)})
        service.get_quotes([ISIN_A])
        provider.quotes = {}  # provider goes dark
        provider.calls.clear()
        row = service.repository.get_by_isin(ISIN_A)
        row.fetched_at = datetime.utcnow() - timedelta(hours=2)
        db_session.commit()

        quotes = service.get_quotes([ISIN_A])

        assert provider.calls == [ISIN_A]
        assert quotes[0].status == "stale"
        assert quotes[0].last_price == Decimal("110.0"), "stale data still served"

    def test_second_provider_used_when_first_fails(self, db_session):
        dead = FakeProvider({})
        alive = FakeProvider({ISIN_A: _quote(ISIN_A, last="55.0", prev="50.0")})
        service = MarketQuoteService(db_session, providers=[dead, alive])

        quotes = service.get_quotes([ISIN_A])

        assert dead.calls == [ISIN_A]
        assert alive.calls == [ISIN_A]
        assert quotes[0].last_price == Decimal("55.0")


class TestDashboard:
    def test_grouping_and_totals(self, db_session):
        _investment(db_session, ISIN_A, "1000.00", date(2026, 11, 1))
        _investment(db_session, ISIN_A, "500.00", date(2026, 11, 10))
        _investment(db_session, ISIN_B, "250.00", date(2026, 11, 15))
        _investment(db_session, None, "999.00", date(2026, 11, 16))
        service, _ = _service(db_session, {
            ISIN_A: _quote(ISIN_A, last="21.5", prev="21.0"),
            ISIN_B: _quote(ISIN_B, last="200.0", prev="200.0"),
        })

        dashboard = service.get_dashboard()

        assert len(dashboard.entries) == 2
        first = dashboard.entries[0]  # ordered by total contributed DESC
        assert first.isin == ISIN_A
        assert first.total_contributed == Decimal("1500.00")
        assert first.contributions == 2
        assert first.last_contribution_date == date(2026, 11, 10)
        assert first.change_pct == Decimal("2.38")  # (21.5-21.0)/21.0*100

        second = dashboard.entries[1]
        assert second.isin == ISIN_B
        assert second.total_contributed == Decimal("250.00")
        assert second.change_abs == Decimal("0.0000")

        assert dashboard.total_contributed == Decimal("1750.00")
        assert dashboard.without_isin_count == 1
        assert dashboard.without_isin_amount == Decimal("999.00")

    def test_soft_deleted_excluded(self, db_session):
        _investment(db_session, ISIN_A, "100.00", date(2026, 11, 1))
        _investment(db_session, ISIN_B, "50.00", date(2026, 11, 2))
        deleted = db_session.execute(
            select(Investment).where(Investment.isin == ISIN_B)
        ).scalars().one()
        deleted.deleted_at = datetime.utcnow()
        db_session.commit()
        service, _ = _service(db_session, {})

        dashboard = service.get_dashboard()

        assert [e.isin for e in dashboard.entries] == [ISIN_A]
        assert dashboard.without_isin_count == 0

    def test_unresolvable_isin_flagged(self, db_session):
        _investment(db_session, ISIN_C, "300.00", date(2026, 11, 1))
        service, _ = _service(db_session, {})  # provider knows nothing

        dashboard = service.get_dashboard()

        assert dashboard.entries[0].isin == ISIN_C
        assert dashboard.entries[0].quote_status == "unavailable"


class TestDashboardPositions:
    """P/L from investment logs (latest snapshot per contribution wins)."""

    def test_units_market_value_and_pl(self, db_session):
        investment = _investment(db_session, ISIN_A, "1000.00", date(2026, 11, 1))
        _log(db_session, investment, date(2026, 11, 1), "10", current_value="1000.00")
        _log(db_session, investment, date(2026, 11, 10), "12", current_value="1200.00")
        service, _ = _service(db_session, {ISIN_A: _quote(ISIN_A, last="110.0", prev="100.0")})

        dashboard = service.get_dashboard()

        entry = dashboard.entries[0]
        assert entry.units == Decimal("12"), "latest log snapshot must win"
        assert entry.market_value == Decimal("1320.00")  # 12 x 110
        assert entry.unrealized_pl == Decimal("320.00")  # 1320 - 1000
        assert entry.unrealized_pl_pct == Decimal("32.00")
        assert entry.reported_value == Decimal("1200.00")
        assert dashboard.total_market_value == Decimal("1320.00")
        assert dashboard.total_unrealized_pl == Decimal("320.00")

    def test_partial_units_flagged(self, db_session):
        logged = _investment(db_session, ISIN_A, "1000.00", date(2026, 11, 1))
        _investment(db_session, ISIN_A, "500.00", date(2026, 11, 5))
        _log(db_session, logged, date(2026, 11, 1), "5", current_value="1000.00")
        service, _ = _service(db_session, {ISIN_A: _quote(ISIN_A, last="110.0", prev="100.0")})

        dashboard = service.get_dashboard()

        entry = dashboard.entries[0]
        assert entry.contributions == 2
        assert entry.units == Decimal("5")
        assert entry.units_partial is True, "one contribution without log must be flagged"
        assert entry.market_value == Decimal("550.00")

    def test_never_logged_is_unknown_not_zero(self, db_session):
        _investment(db_session, ISIN_A, "1000.00", date(2026, 11, 1))
        service, _ = _service(db_session, {ISIN_A: _quote(ISIN_A)})

        dashboard = service.get_dashboard()

        entry = dashboard.entries[0]
        assert entry.units is None, "no logs -> unknown position, NOT 0 units"
        assert entry.market_value is None
        assert entry.unrealized_pl is None
        assert dashboard.total_market_value is None
        assert dashboard.total_unrealized_pl is None

    def test_reported_value_without_quote(self, db_session):
        investment = _investment(db_session, ISIN_B, "250.00", date(2026, 11, 1))
        _log(db_session, investment, date(2026, 11, 1), "3", current_value="260.00")
        service, _ = _service(db_session, {})  # no market data at all

        dashboard = service.get_dashboard()

        entry = dashboard.entries[0]
        assert entry.units == Decimal("3")
        assert entry.reported_value == Decimal("260.00")
        assert entry.market_value is None
        assert entry.quote_status == "unavailable"

    def test_deleted_log_ignored(self, db_session):
        investment = _investment(db_session, ISIN_A, "1000.00", date(2026, 11, 1))
        _log(db_session, investment, date(2026, 11, 1), "8")
        _log(db_session, investment, date(2026, 11, 10), "12")
        log = db_session.execute(
            select(InvestmentLog).where(InvestmentLog.quantity == Decimal("12"))
        ).scalars().one()
        log.deleted_at = datetime.utcnow()
        db_session.commit()
        service, _ = _service(db_session, {ISIN_A: _quote(ISIN_A)})

        dashboard = service.get_dashboard()

        assert dashboard.entries[0].units == Decimal("8")

    def test_positions_across_contributions_sum(self, db_session):
        first = _investment(db_session, ISIN_A, "600.00", date(2026, 11, 1))
        second = _investment(db_session, ISIN_A, "400.00", date(2026, 11, 5))
        _log(db_session, first, date(2026, 11, 1), "6")
        _log(db_session, second, date(2026, 11, 5), "4")
        service, _ = _service(db_session, {ISIN_A: _quote(ISIN_A, last="110.0", prev="100.0")})

        dashboard = service.get_dashboard()

        entry = dashboard.entries[0]
        assert entry.units == Decimal("10")
        assert entry.market_value == Decimal("1100.00")
        assert entry.unrealized_pl == Decimal("100.00")  # 1100 - 1000
        assert entry.units_partial is False
