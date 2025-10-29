from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Enum as SQLEnum
import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class CurrencyEnum(str, enum.Enum):
    euro = "€"
    dolar = "$"
    yuan = "¥"
    bitcoin = "₿"
    ethereum = "Ξ"
    usdc = "USDC"
    dogecoin = "DOGE"
    litecoin = "LTC"
    ripple = "XRP"
    stellar = "XLM"
    cardano = "ADA"
    polkadot = "DOT"
    solana = "SOL"
    shiba_inu = "SHIB"
    tron = "TRX"

class RoleEnum(str, enum.Enum):
    husband = "husband"
    wife = "wife"
    child = "child"
    other = "other"

class ActionEnum(str, enum.Enum):
    buy = "buy"
    sell = "sell"
    transfer = "transfer"
    deposit = "deposit"
    withdraw = "withdraw"
    hold = "hold"

#Define UserRoleEnum for user roles
class UserRoleEnum(str,enum.Enum):
    ADMIN = "administrator"
    EDITOR = "editor"
    USER = "user"
    GUEST = "guest"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    surname1 = Column(String, nullable=False)
    surname2 = Column(String)
    dni = Column(String, nullable=False)
    email = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    telephone = Column(Integer)
    password = Column(String, nullable=False)
    role= Column(SQLEnum(UserRoleEnum), default=UserRoleEnum.USER, nullable=False)


    # Relationships
    expenses = relationship('Expense', back_populates='users')
    incomes = relationship('Income', back_populates='users')
    savings = relationship('Saving', back_populates='users')
    accounts = relationship('Account', back_populates='users')
    investments = relationship('Investment', back_populates='users')
    financials_summaries = relationship('FinancialSummary', back_populates='users')
    households_members = relationship('HouseholdMember', back_populates='users')

class Place(Base):
    __tablename__ = 'places'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(String)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    expenses = relationship('Expense', back_populates='places')

class ExpensesCategory(Base):
    __tablename__ = 'expenses_categories'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    expenses = relationship('Expense', back_populates='categories')

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    place_id = Column(Integer, ForeignKey('places.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('expenses_categories.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='expenses')
    places = relationship('Place', back_populates='expenses')
    categories = relationship('ExpensesCategory', back_populates='expenses')

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    incomes = relationship('Income', back_populates='sources')

class IncomesCategory(Base):
    __tablename__ = 'incomes_categories'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    incomes = relationship('Income', back_populates='categories')

class Income(Base):
    __tablename__ = 'incomes'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('incomes_categories.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='incomes')
    sources = relationship('Source', back_populates='incomes')
    categories = relationship('IncomesCategory', back_populates='incomes')

class Saving(Base):
    __tablename__ = 'savings'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='savings')
    accounts = relationship('Account', back_populates='savings')
    savings_logs = relationship("SavingLog", back_populates="savings")

class SavingLog(Base):
    __tablename__ = "savings_logs"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    total_amount = Column(Float)
    note = Column(String)

    # Foreign Keys
    saving_id = Column(Integer, ForeignKey('savings.id'), nullable=False)

    # Relationships
    savings = relationship('Saving', back_populates="savings_logs")

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    iban = Column(String, nullable=False)
    balance = Column(Float, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='accounts')
    banks = relationship('Bank', back_populates='accounts')
    savings = relationship('Saving', back_populates='accounts')
    investments = relationship('Investment', back_populates='accounts')

class Bank(Base):
    __tablename__ = 'banks'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    accounts = relationship('Account', back_populates='banks')

class InvestmentsCategory(Base):
    __tablename__ = 'investments_categories'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    investments = relationship('Investment', back_populates='categories')

class Investment(Base):
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String)
    amount = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('investments_categories.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='investments')
    accounts = relationship('Account', back_populates='investments')
    categories = relationship('InvestmentsCategory', back_populates='investments')
    investment_logs = relationship('InvestmentLog', back_populates='investments')  # Add this line

class InvestmentLog(Base):
    __tablename__ = "investments_logs"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)
    currentValue = Column(Float, nullable=False)
    pricePerUnit = Column(Float)
    unitsBought = Column(Float)
    action = Column(SQLEnum(ActionEnum), nullable=False)
    note = Column(String)

    # Foreign Keys
    investment_id = Column(Integer, ForeignKey('investments.id'), nullable=False)

    # Relationships
    investments = relationship('Investment', back_populates='investment_logs')

class FinancialSummary(Base):
    __tablename__ = "financials_summaries"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)
    total_income = Column(Float, nullable=False)
    total_expenses = Column(Float, nullable=False)
    total_savings = Column(Float, nullable=False)
    total_investments = Column(Float, nullable=False)
    net_worth = Column(Float, nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    household_id = Column(Integer, ForeignKey('households.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='financials_summaries')

class Household(Base):
    __tablename__ = "households"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    households_members = relationship('HouseholdMember', back_populates='households')

class HouseholdMember(Base):
    __tablename__ = "households_members"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    role = Column(SQLEnum(RoleEnum), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Foreign Keys
    household_id = Column(Integer, ForeignKey('households.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='households_members')
    households = relationship('Household', back_populates='households_members')
