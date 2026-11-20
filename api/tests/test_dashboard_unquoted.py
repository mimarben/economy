"""Dashboard investments WITHOUT ISIN (managed portfolios, crypto, cash).

These investments cannot have a market quote, so the dashboard must still
show them and value them with the hand-recorded valuation (current_value)
of their latest investment log.

All tests run against the in-memory SQLite session from conftest and a
fake provider, so no network access is involved.
"""
from datetime import date, datetime
from decimal import Decimal

from models import Investment, InvestmentLog
from services.investments.market_provider import MarketDataProvider, ProviderQuote
from services.investments.market_quote_service import MarketQuoteService

ISIN_A = "IE00B83YJG36"


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


def _service(db_session, quotes: dict | None = None) -> MarketQuoteService:
    return MarketQuoteService(db_session, providers=[FakeProvider(quotes or {})])


def _investment(db_session, description: str, amount: str, when: date,
                isin: str | None = None, account_id: int = 1) -> Investment:
    investment = Investment(
        description=description,
        date=when,
        currency="EUR",
        amount=Decimal(amount),
        dedup_hash=f"hash-{description}-{when}-{amount}",
        isin=isin,
        account_id=account_id,
        category_id=1,
    )
    db_session.add(investment)
    db_session.commit()
    return investment


def _log(db_session, investment: Investment, when: date, quantity: str,
         current_value: str | None = None) -> None:
    """Position snapshot log; the latest one per investment wins."""
    db_session.add(InvestmentLog(
        investment_id=investment.id,
        date=when,
        current_value=Decimal(current_value) if current_value else None,
        price_per_unit=None,
        quantity=Decimal(quantity),
        action="HOLD",
    ))
    db_session.commit()


class TestUnquotedEntries:
    def test_investment_without_isin_appears_with_manual_valuation(self, db_session):
        """Cartera Naranja / Criptan style: no ISIN, value recorded by hand."""
        inv = _investment(db_session, "Cartera Naranja", "1000.00", date(2026, 1, 10))
        _log(db_session, inv, date(2026, 11, 15), quantity="0", current_value="1120.00")

        dashboard = _service(db_session).get_dashboard()

        assert len(dashboard.unquoted_entries) == 1
        entry = dashboard.unquoted_entries[0]
        assert entry.investment_id == inv.id
        assert entry.name == "Cartera Naranja"
        assert entry.total_contributed == Decimal("1000.00")
        assert entry.reported_value == Decimal("1120.00")
        assert entry.value == Decimal("1120.00")
        assert entry.unrealized_pl == Decimal("120.00")
        # KPIs now include the manual valuation
        assert dashboard.total_reported_value == Decimal("1120.00")
        assert dashboard.total_reported_pl == Decimal("120.00")

    def test_total_contributed_includes_unquoted_investments(self, db_session):
        """Before this fix the total aportado KPI ignored no-ISIN investments."""
        _investment(db_session, "Criptan BTC", "500.00", date(2026, 2, 1))

        dashboard = _service(db_session).get_dashboard()

        assert dashboard.total_contributed == Decimal("500.00")
        assert dashboard.without_isin_count == 1

    def test_unquoted_without_log_has_no_valuation_but_is_listed(self, db_session):
        _investment(db_session, "Criptan ETH", "300.00", date(2026, 3, 1))

        dashboard = _service(db_session).get_dashboard()

        assert len(dashboard.unquoted_entries) == 1
        entry = dashboard.unquoted_entries[0]
        assert entry.units is None
        assert entry.reported_value is None
        assert entry.value is None
        assert entry.unrealized_pl is None
        assert dashboard.total_reported_value is None
        assert dashboard.total_reported_pl is None

    def test_latest_log_wins_for_manual_valuation(self, db_session):
        inv = _investment(db_session, "Cartera Naranja", "1000.00", date(2026, 1, 10))
        _log(db_session, inv, date(2026, 6, 30), quantity="0", current_value="1050.00")
        _log(db_session, inv, date(2026, 11, 15), quantity="0", current_value="1180.00")

        dashboard = _service(db_session).get_dashboard()

        assert dashboard.unquoted_entries[0].reported_value == Decimal("1180.00")

    def test_soft_deleted_unquoted_investment_excluded(self, db_session):
        inv = _investment(db_session, "Cartera vieja", "100.00", date(2026, 1, 10))
        inv.deleted_at = datetime(2026, 2, 1)
        db_session.commit()

        dashboard = _service(db_session).get_dashboard()

        assert dashboard.unquoted_entries == []
        assert dashboard.total_contributed == Decimal("0")

    def test_isin_entries_are_not_duplicated_as_unquoted(self, db_session):
        _investment(db_session, "Fondo con ISIN", "1000.00", date(2026, 1, 10),
                    isin=ISIN_A)

        dashboard = _service(db_session).get_dashboard()

        assert dashboard.unquoted_entries == []
        assert len(dashboard.entries) == 1
        assert dashboard.entries[0].isin == ISIN_A

    def test_crypto_currency_renders_as_plain_code(self, db_session):
        """CurrencyEnum crypto values are tuples; the API must return 'BTC'."""
        inv = Investment(
            description="Criptan BTC",
            date=date(2026, 2, 1),
            currency="BTC",
            amount=Decimal("0.5"),
            dedup_hash="hash-btc-1",
            isin=None,
            account_id=1,
            category_id=1,
        )
        db_session.add(inv)
        db_session.commit()

        dashboard = _service(db_session).get_dashboard()

        assert dashboard.unquoted_entries[0].currency == "BTC"


class TestUnquotedScoping:
    """D8: regular users only see their accounts; admin (None) sees all."""

    def _seed_users_and_accounts(self, db_session):
        from models import Account, AccountUser, Bank, User, UserRoleEnum
        from services.core.security_service import hash_password

        user1 = User(name="U1", surname1="T", dni="11111111H", email="u1@test.com",
                     active=True, password=hash_password("Password1!"), role=UserRoleEnum.USER)
        user2 = User(name="U2", surname1="T", dni="22222222J", email="u2@test.com",
                     active=True, password=hash_password("Password1!"), role=UserRoleEnum.USER)
        db_session.add_all([user1, user2])
        db_session.commit()

        bank = Bank(name="Test Bank", description="T", active=True, cif="B12345678")
        db_session.add(bank)
        db_session.commit()

        account1 = Account(name="A1", iban="ES1111111111111111111111",
                           currency="EUR", active=True, bank_id=bank.id)
        account2 = Account(name="A2", iban="ES2222222222222222222222",
                           currency="EUR", active=True, bank_id=bank.id)
        db_session.add_all([account1, account2])
        db_session.commit()
        db_session.add_all([
            AccountUser(account_id=account1.id, user_id=user1.id),
            AccountUser(account_id=account2.id, user_id=user2.id),
        ])
        db_session.commit()
        return user1, user2, account1, account2

    def test_unquoted_filtered_by_user(self, db_session):
        user1, user2, account1, account2 = self._seed_users_and_accounts(db_session)
        _investment(db_session, "Cartera User1", "1000.00", date(2026, 1, 10),
                    account_id=account1.id)
        _investment(db_session, "Cripto User2", "2000.00", date(2026, 1, 10),
                    account_id=account2.id)

        service = _service(db_session)

        user1_dash = service.get_dashboard(user_id=user1.id)
        assert [e.name for e in user1_dash.unquoted_entries] == ["Cartera User1"]
        assert user1_dash.total_contributed == Decimal("1000.00")

        user2_dash = service.get_dashboard(user_id=user2.id)
        assert [e.name for e in user2_dash.unquoted_entries] == ["Cripto User2"]

        admin_dash = service.get_dashboard(user_id=None)
        assert len(admin_dash.unquoted_entries) == 2
        assert admin_dash.total_contributed == Decimal("3000.00")
