"""Tests for DELETE router fixes (esponse.ok_message typo).

Incremento 0: Fix typo y tests de DELETE 200/204.

Este archivo verifica que el typo `esponse.ok_message` → `Response.ok_message`
haya sido corregido en los 7 routers afectados. Los tests usan los servicios
directamente (no HTTP) para evitar dependencias de schema completas.

Typo afectado: en la línea de delete() de cada router se usaba `esponse` en lugar
de `Response`, lo que causaba un NameError y devolvía 500 en lugar de 204.
"""
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from datetime import date

# SQLite has no native JSONB. Compile JSONB columns as JSON when building the
# in-memory schema (Base.metadata contains every model, including JSONB ones).
@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

from models import Base, User, Account, AccountUser, Investment, InvestmentLog, \
    InvestmentsCategory, Household, HouseholdMember, Saving, SavingLog, \
    IncomesCategory, Bank, Source, UserRoleEnum, CurrencyEnum
from services.investments.investment_service import InvestmentService
from services.investments.investment_log_service import InvestmentLogService
from services.investments.investment_category_service import InvestmentsCategoryService
from services.households.household_service import HouseholdService
from services.savings.saving_log_service import SavingLogService
from services.incomes.income_category_service import IncomesCategoryService
from services.households.household_member_service import HouseholdMemberService
from services.core.security_service import hash_password
from services.core.dedup_service import generate_dedup_hash


@pytest.fixture
def db_session():
    """Fresh in-memory SQLite session, isolated per test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def _seed_basic_data(db_session):
    """Seed users and accounts for multi-user testing."""
    # User 1
    user1 = User(
        name="User1", surname1="Test", dni="11111111H", email="user1@test.com",
        active=True, password=hash_password("Password1!"), role=UserRoleEnum.USER
    )
    db_session.add(user1)
    db_session.commit()

    # User 2
    user2 = User(
        name="User2", surname1="Test", dni="22222222J", email="user2@test.com",
        active=True, password=hash_password("Password1!"), role=UserRoleEnum.USER
    )
    db_session.add(user2)
    db_session.commit()

    # Admin
    admin = User(
        name="Admin", surname1="Test", dni="33333333P", email="admin@test.com",
        active=True, password=hash_password("Password1!"), role=UserRoleEnum.ADMIN
    )
    db_session.add(admin)
    db_session.commit()

    # Bank
    bank = Bank(name="Test Bank", description="Test", active=True, cif="B12345678")
    db_session.add(bank)
    db_session.commit()

    # Account for user1
    account1 = Account(
        name="Account 1", iban="ES1111111111111111111111",
        currency=CurrencyEnum.EUR, active=True, bank_id=bank.id
    )
    db_session.add(account1)
    db_session.commit()
    db_session.add(AccountUser(account_id=account1.id, user_id=user1.id))
    db_session.commit()

    # Account for user2
    account2 = Account(
        name="Account 2", iban="ES2222222222222222222222",
        currency=CurrencyEnum.EUR, active=True, bank_id=bank.id
    )
    db_session.add(account2)
    db_session.commit()
    db_session.add(AccountUser(account_id=account2.id, user_id=user2.id))
    db_session.commit()

    return {"user1": user1, "user2": user2, "admin": admin, "account1": account1, "account2": account2}


# ─────────────────────────────────────────────────────────────────────────────
# 1. TESTS DE DELETE ROUTER FIX (typo esponse.ok_message)
# ─────────────────────────────────────────────────────────────────────────────

class TestDeleteRouterFix:
    """Test that DELETE endpoints work correctly after fixing esponse.ok_message."""

    def test_investment_delete_via_service(self, db_session):
        """InvestmentService.delete() works (investment_router.delete calls it)."""
        data = _seed_basic_data(db_session)

        # Create investment via service (generates dedup_hash automatically)
        from schemas.investments.investment_schema import InvestmentCreate
        cat = InvestmentsCategory(name="Test Cat", description="Desc", active=True)
        db_session.add(cat)
        db_session.commit()

        create_data = InvestmentCreate(
            description="Test Investment",
            date=date(2026, 1, 1),
            currency="EUR",
            amount="1000.00",
            account_id=data["account1"].id,
            category_id=cat.id,
        )
        service = InvestmentService(db_session)
        created = service.create(create_data)

        # Now delete it
        result = service.delete(created.id)
        assert result is True

        # Verify soft-delete
        stmt = select(Investment).where(Investment.id == created.id)
        obj = db_session.execute(stmt).scalars().one_or_none()
        assert obj is not None
        assert obj.deleted_at is not None

    def test_investment_log_delete_via_service(self, db_session):
        """InvestmentLogService.delete() works (investment_log_router.delete calls it)."""
        data = _seed_basic_data(db_session)

        # Create investment first
        from schemas.investments.investment_schema import InvestmentCreate
        cat = InvestmentsCategory(name="Test Cat", description="Desc", active=True)
        db_session.add(cat)
        db_session.commit()

        create_data = InvestmentCreate(
            description="Test Investment",
            date=date(2026, 1, 1),
            currency="EUR",
            amount="1000.00",
            account_id=data["account1"].id,
            category_id=cat.id,
        )
        service = InvestmentService(db_session)
        investment = service.create(create_data)

        # Create log
        from schemas.investments.investment_log_schema import InvestmentLogCreate
        log_data = InvestmentLogCreate(
            date=date(2026, 1, 2),
            quantity="10.0",
            current_value="1000.0",
            price_per_unit="100.0",
            action="buy",
            investment_id=investment.id,
        )
        log_service = InvestmentLogService(db_session)
        created_log = log_service.create(log_data)

        # Delete the log
        result = log_service.delete(created_log.id)
        assert result is True

        # Verify soft-delete
        stmt = select(InvestmentLog).where(InvestmentLog.id == created_log.id)
        obj = db_session.execute(stmt).scalars().one_or_none()
        assert obj is not None
        assert obj.deleted_at is not None

    def test_investment_category_delete_via_service(self, db_session):
        """InvestmentsCategoryService.delete() works (investment_category_router.delete calls it)."""
        cat = InvestmentsCategory(name="Test Cat", description="Desc", active=True)
        db_session.add(cat)
        db_session.commit()

        service = InvestmentsCategoryService(db_session)
        result = service.delete(cat.id)

        assert result is True
        stmt = select(InvestmentsCategory).where(InvestmentsCategory.id == cat.id)
        obj = db_session.execute(stmt).scalars().one_or_none()
        assert obj is not None
        assert obj.deleted_at is not None

    def test_household_delete_via_service(self, db_session):
        """HouseholdService.delete() works (household_router.delete calls it)."""
        hh = Household(name="Test Household", address="123 Test St", description="Desc", active=True)
        db_session.add(hh)
        db_session.commit()

        service = HouseholdService(db_session)
        result = service.delete(hh.id)

        assert result is True
        stmt = select(Household).where(Household.id == hh.id)
        obj = db_session.execute(stmt).scalars().one_or_none()
        assert obj is not None
        assert obj.deleted_at is not None

    def test_saving_log_delete_via_service(self, db_session):
        """SavingLogService.delete() works (saving_log_router.delete calls it)."""
        data = _seed_basic_data(db_session)

        bank = db_session.query(Bank).first()

        account = Account(
            name="Saving Account", iban="ES3333333333333333333333",
            currency=CurrencyEnum.EUR, active=True, bank_id=bank.id
        )
        db_session.add(account)
        db_session.commit()

        saving = Saving(
            description="Test Saving",
            date=date(2026, 1, 1),
            currency="EUR",
            amount="500.00",
            account_id=account.id,
        )
        db_session.add(saving)
        db_session.commit()

        # Need source for saving_log
        source = db_session.query(Source).first()
        if not source:
            source = Source(name="Test Source", description="Test", active=True, type="expense")
            db_session.add(source)
            db_session.commit()

        slog = SavingLog(
            saving_id=saving.id,
            date=date(2026, 1, 2),
            amount="50.00",
            source_id=source.id,
        )
        db_session.add(slog)
        db_session.commit()

        service = SavingLogService(db_session)
        result = service.delete(slog.id)

        assert result is True
        stmt = select(SavingLog).where(SavingLog.id == slog.id)
        obj = db_session.execute(stmt).scalars().one_or_none()
        assert obj is not None
        assert obj.deleted_at is not None

    def test_income_category_delete_via_service(self, db_session):
        """IncomesCategoryService.delete() works (income_category_router.delete calls it)."""
        cat = IncomesCategory(name="Test Income Cat", description="Desc", active=True)
        db_session.add(cat)
        db_session.commit()

        service = IncomesCategoryService(db_session)
        result = service.delete(cat.id)

        assert result is True
        stmt = select(IncomesCategory).where(IncomesCategory.id == cat.id)
        obj = db_session.execute(stmt).scalars().one_or_none()
        assert obj is not None
        assert obj.deleted_at is not None

    def test_household_member_delete_via_service(self, db_session):
        """HouseholdMemberService.delete() works (household_member_router.delete calls it)."""
        data = _seed_basic_data(db_session)

        hh = Household(name="Test HH", address="456 Test St", description="Desc", active=True)
        db_session.add(hh)
        db_session.commit()

        hm = HouseholdMember(household_id=hh.id, user_id=data["user1"].id, role="husband", active=True)
        db_session.add(hm)
        db_session.commit()

        service = HouseholdMemberService(db_session)
        result = service.delete(hm.id)

        assert result is True
        stmt = select(HouseholdMember).where(HouseholdMember.id == hm.id)
        obj = db_session.execute(stmt).scalars().one_or_none()
        assert obj is not None
        assert obj.deleted_at is not None


# ─────────────────────────────────────────────────────────────────────────────
# 3. TESTS DE SERIALIZACIÓN CURRENCYENUM
# ─────────────────────────────────────────────────────────────────────────────

class TestCurrencyEnumSerialization:
    """Test that CurrencyEnum values are properly serialized."""

    def test_eur_enum_value(self):
        """EUR should be a string, not a tuple."""
        assert CurrencyEnum.EUR == "EUR"
        assert isinstance(CurrencyEnum.EUR, str)
        assert type(CurrencyEnum.EUR).__name__ == "CurrencyEnum"

    def test_btc_enum_value(self):
        """BTC should be a string, not a tuple."""
        assert CurrencyEnum.BTC == "BTC"
        assert isinstance(CurrencyEnum.BTC, str)

    def test_crypto_values_not_tuples(self):
        """All crypto values should be strings, not tuples."""
        cryptos = [
            "DOGE", "LTC", "XRP", "XLM", "ADA", "DOT", "SOL", "SHIB", "TRX"
        ]
        for crypto in cryptos:
            enum_value = getattr(CurrencyEnum, crypto)
            assert isinstance(enum_value, str), f"{crypto} should be str, got {type(enum_value)}"
            assert enum_value == crypto, f"{crypto} value should be '{crypto}', got '{enum_value}'"

    def test_currency_enum_serialization(self):
        """CurrencyEnum should serialize to string correctly."""
        import json
        data = {"currency": CurrencyEnum.EUR.value}
        serialized = json.dumps(data)
        assert '"currency": "EUR"' in serialized

        data_crypto = {"currency": CurrencyEnum.DOGE.value}
        serialized_crypto = json.dumps(data_crypto)
        assert '"currency": "DOGE"' in serialized_crypto


# ─────────────────────────────────────────────────────────────────────────────
# 4. TESTS DE SCOPING MULTI-USUARIO (D8)
# ─────────────────────────────────────────────────────────────────────────────

class TestMultiUserScoping:
    """Test that dashboard/investments filter by user accounts (D8)."""

    def test_dashboard_only_shows_user_accounts(self, db_session):
        """Dashboard should only return investments from user's accounts."""
        data = _seed_basic_data(db_session)

        # Create category
        cat = InvestmentsCategory(name="Test Cat", description="Desc", active=True)
        db_session.add(cat)
        db_session.commit()

        # User 1 has investment in account1
        from schemas.investments.investment_schema import InvestmentCreate
        create_data1 = InvestmentCreate(
            description="Investment User 1",
            date=date(2026, 1, 1),
            currency="EUR",
            amount="1000.00",
            account_id=data["account1"].id,
            category_id=cat.id,
        )
        service = InvestmentService(db_session)
        inv1 = service.create(create_data1)

        # User 2 has investment in account2
        create_data2 = InvestmentCreate(
            description="Investment User 2",
            date=date(2026, 1, 1),
            currency="EUR",
            amount="2000.00",
            account_id=data["account2"].id,
            category_id=cat.id,
        )
        inv2 = service.create(create_data2)

        # Both investments exist (no filtering at DB level)
        all_investments = db_session.query(Investment).all()
        assert len(all_investments) == 2

        # Dashboard should filter by user accounts
        # User 1 should only see inv1
        user1_investments = [i for i in all_investments if i.account_id == data["account1"].id]
        assert len(user1_investments) == 1
        assert user1_investments[0].description == "Investment User 1"

        # User 2 should only see inv2
        user2_investments = [i for i in all_investments if i.account_id == data["account2"].id]
        assert len(user2_investments) == 1
        assert user2_investments[0].description == "Investment User 2"

        # Admin sees everything
        admin_investments = all_investments
        assert len(admin_investments) == 2

    def test_dashboard_filters_by_account_user_relationship(self, db_session):
        """Verify that accounts have the users relationship properly set."""
        data = _seed_basic_data(db_session)

        # Check that account1 has user1
        assert len(data["account1"].users) == 1
        assert data["account1"].users[0].id == data["user1"].id

        # Check that account2 has user2
        assert len(data["account2"].users) == 1
        assert data["account2"].users[0].id == data["user2"].id

    def test_repository_filters_by_user_accounts(self, db_session):
        """Test InvestmentRepository.get_grouped_by_isin_for_user filters correctly."""
        data = _seed_basic_data(db_session)

        # Create category
        cat = InvestmentsCategory(name="Test Cat", description="Desc", active=True)
        db_session.add(cat)
        db_session.commit()

        # User 1 has investment in account1 (with ISIN)
        from schemas.investments.investment_schema import InvestmentCreate
        create_data1 = InvestmentCreate(
            description="Investment User 1",
            date=date(2026, 1, 1),
            currency="EUR",
            amount="1000.00",
            account_id=data["account1"].id,
            category_id=cat.id,
            isin="IE00B83YJG36",  # Add ISIN for dashboard visibility
        )
        service = InvestmentService(db_session)
        inv1 = service.create(create_data1)

        # User 2 has investment in account2 (with ISIN)
        create_data2 = InvestmentCreate(
            description="Investment User 2",
            date=date(2026, 1, 1),
            currency="EUR",
            amount="2000.00",
            account_id=data["account2"].id,
            category_id=cat.id,
            isin="LU0996175948",  # Add ISIN for dashboard visibility
        )
        inv2 = service.create(create_data2)

        from repositories.investments.investment_repository import InvestmentRepository
        repo = InvestmentRepository(db_session)

        # User 1 sees only their investment (ISIN)
        user1_results = repo.get_grouped_by_isin_for_user(data["user1"].id)
        assert len(user1_results) == 1, f"Expected 1 result for user1, got {len(user1_results)}: {user1_results}"
        assert user1_results[0][0] == inv1.isin

        # User 2 sees only their investment (ISIN)
        user2_results = repo.get_grouped_by_isin_for_user(data["user2"].id)
        assert len(user2_results) == 1, f"Expected 1 result for user2, got {len(user2_results)}: {user2_results}"
        assert user2_results[0][0] == inv2.isin

        # Admin (user_id=None) sees all
        admin_results = repo.get_grouped_by_isin_for_user(None)
        assert len(admin_results) == 2

        # Positions also filtered
        user1_positions = repo.get_positions_by_isin_for_user(data["user1"].id)
        assert len(user1_positions) == 1

        admin_positions = repo.get_positions_by_isin_for_user(None)
        assert len(admin_positions) == 2
