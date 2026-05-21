import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB

# SQLite does not support PostgreSQL JSONB natively. Register a custom compiler.
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

from models import (
    Base, User, Bank, Account, Source, IncomesCategory, ExpensesCategory,
    Expense, Income, UserRoleEnum, CurrencyEnum, SourceTypeEnum
)
from schemas.imports.import_schema import BulkImportRequest, ExpenseImportCreate, IncomeImportCreate
from services.imports.import_service import ImportService


@pytest.fixture

def db_session():
    # Set up an in-memory SQLite database
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
    # 1. Create a user
    user = User(
        name="Test",
        surname1="User",
        surname2="Demo",
        dni="12345678A",
        email="test@user.com",
        active=True,
        password="hashed_password",
        role=UserRoleEnum.ADMIN
    )
    db_session.add(user)
    
    # 2. Create a bank
    bank = Bank(
        name="Test Bank",
        description="A test bank",
        active=True,
        cif="A1234567B"
    )
    db_session.add(bank)
    db_session.commit()
    
    # 3. Create an account
    account = Account(
        name="Test Account",
        description="Checking account",
        iban="ES12345678901234567890",
        balance=1000.0,
        active=True,
        bank_id=bank.id,
        currency=CurrencyEnum.EUR
    )
    db_session.add(account)
    db_session.commit()
    
    # Associate user and account
    from models import AccountUser
    db_session.add(AccountUser(account_id=account.id, user_id=user.id))
    db_session.commit()
    
    # 4. Create sources for expense and income
    source_expense = Source(
        name="Supermarket",
        description="Groceries",
        active=True,
        type=SourceTypeEnum.EXPENSE
    )
    source_income = Source(
        name="Salary Source",
        description="Monthly Salary",
        active=True,
        type=SourceTypeEnum.INCOME
    )
    db_session.add_all([source_expense, source_income])
    
    # 5. Create categories
    expense_category = ExpensesCategory(
        name="Food",
        description="Groceries & Dining",
        active=True
    )
    income_category = IncomesCategory(
        name="Salary",
        description="Job income",
        active=True
    )
    db_session.add_all([expense_category, income_category])
    db_session.commit()
    
    return {
        "user_id": user.id,
        "account_id": account.id,
        "expense_source_id": source_expense.id,
        "income_source_id": source_income.id,
        "expense_category_id": expense_category.id,
        "income_category_id": income_category.id
    }


def test_import_transactions_atomic_success(db_session, seed_data):
    # Prepare payload with 1 expense and 1 income
    payload = BulkImportRequest(
        expenses=[
            ExpenseImportCreate(
                name="Grocery shopping",
                description="Bought milk and bread",
                amount=25.50,
                date="2026-05-20T10:00:00",
                currency="EUR",
                user_id=seed_data["user_id"],
                source_id=seed_data["expense_source_id"],
                category_id=seed_data["expense_category_id"],
                account_id=seed_data["account_id"],
                ignore_in_analysis=False
            )
        ],
        incomes=[
            IncomeImportCreate(
                name="Monthly Salary",
                description="Salary payment May 2026",
                amount=2500.00,
                date="2026-05-20T09:00:00",
                currency="EUR",
                source_id=seed_data["income_source_id"],
                category_id=seed_data["income_category_id"],
                account_id=seed_data["account_id"],
                ignore_in_analysis=False
            )
        ],
        auto_categorize=False
    )
    
    service = ImportService(db_session)
    result = service.import_transactions_atomic(payload)
    
    # Verify return counts
    assert result["inserted"] == 2
    assert result["duplicates"] == 0
    assert result["total"] == 2
    
    # Verify in DB
    expenses_in_db = db_session.query(Expense).all()
    assert len(expenses_in_db) == 1
    assert expenses_in_db[0].amount == 25.50
    assert expenses_in_db[0].description == "Bought milk and bread"
    assert expenses_in_db[0].name == "Grocery shopping"
    
    incomes_in_db = db_session.query(Income).all()
    assert len(incomes_in_db) == 1
    assert incomes_in_db[0].amount == 2500.00
    assert incomes_in_db[0].description == "Salary payment May 2026"
    assert incomes_in_db[0].ignore_in_analysis is False


def test_import_transactions_atomic_duplicate_handling(db_session, seed_data):
    service = ImportService(db_session)
    
    payload1 = BulkImportRequest(
        expenses=[
            ExpenseImportCreate(
                name="Coffee",
                description="Morning coffee",
                amount=2.50,
                date="2026-05-20T08:00:00",
                currency="EUR",
                user_id=seed_data["user_id"],
                source_id=seed_data["expense_source_id"],
                category_id=seed_data["expense_category_id"],
                account_id=seed_data["account_id"],
                ignore_in_analysis=False
            )
        ],
        incomes=[],
        auto_categorize=False
    )
    
    # First import - successful
    res1 = service.import_transactions_atomic(payload1)
    assert res1["inserted"] == 1
    assert res1["duplicates"] == 0
    
    # Second import with identical transaction - detected as duplicate
    res2 = service.import_transactions_atomic(payload1)
    assert res2["inserted"] == 0
    assert res2["duplicates"] == 1
    
    # Verify only 1 exists in DB
    expenses_in_db = db_session.query(Expense).all()
    assert len(expenses_in_db) == 1


def test_import_transactions_atomic_fk_error(db_session, seed_data):
    # Payload with invalid category ID
    payload = BulkImportRequest(
        expenses=[
            ExpenseImportCreate(
                name="Grocery shopping",
                description="Bought milk and bread",
                amount=25.50,
                date="2026-05-20T10:00:00",
                currency="EUR",
                user_id=seed_data["user_id"],
                source_id=seed_data["expense_source_id"],
                category_id=9999,  # Non-existent category
                account_id=seed_data["account_id"],
                ignore_in_analysis=False
            )
        ],
        incomes=[],
        auto_categorize=False
    )
    
    service = ImportService(db_session)
    
    # Should raise ValueError and fail transaction
    with pytest.raises(ValueError) as exc_info:
        service.import_transactions_atomic(payload)
        
    assert "Expense FK error" in str(exc_info.value)
    
    # Verify nothing was added
    assert len(db_session.query(Expense).all()) == 0
