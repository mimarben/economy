"""Tests for automatic rule learning on category correction (expenses)."""
import pytest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


from models import (
    Base, User, Bank, Account, Source, IncomesCategory, ExpensesCategory,
    Expense, CategoryRule, UserRoleEnum, CurrencyEnum, SourceTypeEnum,
)
from schemas.expenses.expense_schema import ExpenseCreate, ExpenseUpdate
from services.expenses.expense_service import ExpenseService
from services.rules.categorization_service import CategorizationService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def seed_data(db_session):
    user = User(
        name="Test", surname1="User", surname2="", dni="11111111A",
        email="test@user.com", active=True, password="x", role=UserRoleEnum.ADMIN,
    )
    bank = Bank(name="Test Bank", description="", active=True, cif="B1234567C")
    db_session.add_all([user, bank])
    db_session.commit()

    account = Account(
        name="Acc", description="", iban="ES1111111111111111111111",
        balance=0.0, active=True, bank_id=bank.id, currency=CurrencyEnum.EUR,
    )
    db_session.add(account)
    db_session.commit()

    source = Source(name="Shop", description="", active=True, type=SourceTypeEnum.EXPENSE)
    cat_a = ExpensesCategory(name="Otros", description="", active=True)
    cat_b = ExpensesCategory(name="Supermercado", description="", active=True)
    db_session.add_all([source, cat_a, cat_b])
    db_session.commit()

    return {
        "user_id": user.id,
        "account_id": account.id,
        "source_id": source.id,
        "cat_a": cat_a.id,
        "cat_b": cat_b.id,
    }


def _make_expense(db_session, seed_data, description="MERCADONA COMPRA 123"):
    from services.core.dedup_service import generate_dedup_hash

    expense = Expense(
        name=description,
        description=description,
        amount=10.0,
        date=date(2026, 5, 20),
        currency=CurrencyEnum.EUR,
        source_id=seed_data["source_id"],
        category_id=seed_data["cat_a"],
        account_id=seed_data["account_id"],
        # ExpenseRead requires user_id for personal expenses: mirror the real
        # app, where imports/edits always assign the current user.
        is_personal=True,
        user_id=seed_data["user_id"],
        ignore_in_analysis=False,
        dedup_hash=generate_dedup_hash(
            account_id=seed_data["account_id"],
            txn_date=date(2026, 5, 20),
            amount=10.0,
            description=description,
        ),
    )
    db_session.add(expense)
    db_session.commit()
    return expense


def test_category_correction_learns_rule(db_session, seed_data):
    expense = _make_expense(db_session, seed_data)
    service = ExpenseService(db_session)

    updated = service.update(expense.id, ExpenseUpdate(category_id=seed_data["cat_b"]))
    assert updated is not None
    assert updated.category_id == seed_data["cat_b"]

    # A learned rule must exist and classify the description automatically
    rules = db_session.query(CategoryRule).all()
    assert len(rules) == 1
    assert rules[0].category_id == seed_data["cat_b"]
    assert rules[0].priority == 10
    assert rules[0].is_active is True

    categorizer = CategorizationService(db_session)
    assert categorizer.categorize_transaction(
        description="MERCADONA COMPRA 123", transaction_type="expense"
    ) == seed_data["cat_b"]


def test_no_rule_learned_when_category_unchanged(db_session, seed_data):
    expense = _make_expense(db_session, seed_data)
    service = ExpenseService(db_session)

    service.update(expense.id, ExpenseUpdate(category_id=seed_data["cat_a"]))

    assert db_session.query(CategoryRule).count() == 0


def test_no_duplicate_rule_learned(db_session, seed_data):
    expense = _make_expense(db_session, seed_data)
    service = ExpenseService(db_session)

    service.update(expense.id, ExpenseUpdate(category_id=seed_data["cat_b"]))

    # Second correction of the same description (via another expense row):
    # the existing rule already covers it, no new rule should be created.
    from services.core.dedup_service import generate_dedup_hash
    e3 = Expense(
        name="MERCADONA COMPRA 123", description="MERCADONA COMPRA 123",
        amount=99.0, date=date(2026, 5, 21), currency=CurrencyEnum.EUR,
        source_id=seed_data["source_id"], category_id=seed_data["cat_a"],
        account_id=seed_data["account_id"], is_personal=True,
        user_id=seed_data["user_id"], ignore_in_analysis=False,
        dedup_hash=generate_dedup_hash(
            account_id=seed_data["account_id"], txn_date=date(2026, 5, 21),
            amount=99.0, description="MERCADONA COMPRA 123",
        ),
    )
    db_session.add(e3)
    db_session.commit()

    service.update(e3.id, ExpenseUpdate(category_id=seed_data["cat_b"]))
    assert db_session.query(CategoryRule).count() == 1
