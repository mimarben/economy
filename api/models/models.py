from sqlalchemy import create_engine, Column, Integer, String,  Float, Date, Boolean,  ForeignKey, Enum as SQLEnum
import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, declarative_base
import os
Base = declarative_base()

from enum import Enum



class CurrencyEnum(enum.Enum):
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
class RoleEnum(enum.Enum):
    husband = "husband"
    wife= "wife"
    child = "child"
    other = "other"

class User(Base):  # Singular name for consistency
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String,  nullable=False)
    surname1 = Column(String,  nullable=False)
    surname2 = Column(String)
    dni = Column(String,  nullable=False)
    email = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    telephone = Column(Integer)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False) 

    # Relationships
    expenses = relationship('Expense', back_populates='user')
    incomes = relationship('Income', back_populates='user')
    savings = relationship('Saving', back_populates='user')
    accounts = relationship('Account', back_populates='user')
    investments = relationship('Investment', back_populates='user')

class Place(Base):  # Singular name for consistency
    __tablename__ = 'places'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String,nullable=False)
    address = Column(String)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    expenses = relationship('Expense', back_populates='place')


class ExpensesCategory(Base):  # Singular name for consistency
    __tablename__ = 'expenses_categories'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    # Relationships
    expenses = relationship('Expense', back_populates='category')

class Expense(Base):  # Singular name for consistency
    __tablename__ = 'expenses'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Float, nullable=False)  # Changed to Float for decimal amounts
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False) 

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'),nullable=False)
    place_id = Column(Integer, ForeignKey('places.id'),nullable=False)
    category_id = Column(Integer, ForeignKey('expenses_categories.id'),nullable=False)

    # Relationships
    user = relationship('User', back_populates='expenses')
    place = relationship('Place', back_populates='expenses')
    category = relationship('ExpensesCategory', back_populates='expenses')

class Source(Base):  # Singular name for consistency
    __tablename__ = 'sources'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    # Relationships
    incomes = relationship('Income', back_populates='source')


class IcomesCategory(Base):  # Singular name for consistency
    __tablename__ = 'incomes_categories'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    # Relationships
    incomes = relationship('Income', back_populates='category')

class Income(Base):  # Singular name for consistency
    __tablename__ = 'incomes'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Float, nullable=False)  # Float for decimal amounts
    date = Column(Date , nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'))
    source_id = Column(Integer, ForeignKey('sources.id'))
    category_id = Column(Integer, ForeignKey('incomes_categories.id'))

    # Relationships
    user = relationship('User', back_populates='incomes')
    source = relationship('Source', back_populates='incomes')
    category = relationship('IcomesCategory', back_populates='incomes')


class Saving(Base):  # Singular name for consistency
    __tablename__ = 'savings'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Float, nullable=False)  # Float for decimal amounts
    date = Column(Date, nullable=False)  # Changed to Date for consistency
    currency = Column(SQLEnum(CurrencyEnum), nullable=False) 
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))

    # Relationships
    user = relationship('User', back_populates='savings')
    account = relationship('Account', back_populates='savings')

class SavingLog(Base):
    __tablename__ = "savings_logs"
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)  # Changed to Date for consistency
    amount = Column(Float, nullable=False)  # Float for decimal amounts
    total_amount = Column(Float)  # Float for decimal amounts
    note= Column(String)

    # Foreign Keys
    saving_id = Column(Integer, ForeignKey('saving.id'))
    
    # Relationships
    saving = relationship('Saving', back_populates='savings_logs')


class Account(Base):  # Singular name for consistency
    __tablename__ = 'accounts'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    iban = Column(String, nullable=False)
    balance = Column(Float, nullable=False)  # Float for decimal amounts

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'))
    bank_id = Column(Integer, ForeignKey('banks.id'))

    # Relationships
    user = relationship('User', back_populates='accounts')
    bank = relationship('Bank', back_populates='accounts')
    savings = relationship('Saving', back_populates='accounts')
    investments = relationship('Investment', back_populates='accounts')

class Bank(Base):  # Singular name for consistency
    __tablename__ = 'banks'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    # Relationships
    accounts = relationship('Account', back_populates='banks')  # One-to-Many relationship with accounts

class InvestmentsCategory(Base):  # Singular name for consistency
    __tablename__ = 'investments_categories'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    # Relationships
    investments = relationship('Investment', back_populates='category')


class Investment(Base):  # Singular name for consistency
    __tablename__ = 'investments'
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String)
    description = Column(String)
    amount = Column(Float, nullable=False)  # Float for decimal amounts
    value = Column(Float, nullable=False)  # Float for investment value
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False) 
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    category_id = Column(Integer, ForeignKey('investments_categories.id'))

    # Relationships
    user = relationship('User', back_populates='investments')
    account = relationship('Account', back_populates='investments')
    category = relationship('InvestmentsCategory', back_populates='investments')

class InvestmentLog(Base):
    __tablename__ = "investments_logs"
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)  # Changed to Date for consistency
    currentValue = Column(Float, nullable=False)  # Float for decimal amounts
    amount = Column(Float)  # Float for decimal amounts
    note= Column(String)

    # Foreign Keys
    investment_id = Column(Integer, ForeignKey('saving.id'))
    
    # Relationships
    investment = relationship('Investment', back_populates='investments')

class Household (Base):
    __tablename__ = "households"
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    name = Column(String), nullable=False
    address = Column(String, nullable=False)
    description = Column(String)

class HouseholdMember(Base):
    __tablename__ = "households_members"
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True)
    role = Column(SQLEnum(RoleEnum), nullable=False) 
    # Foreign Keys
    household_id = Column(Integer, ForeignKey('households.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    user = relationship('User', back_populates='households_members')
    household= relationship('Household', back_populates='households_members')