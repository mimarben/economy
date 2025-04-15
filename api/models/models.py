from sqlalchemy import create_engine, Column, Integer, String,  Float, Date,  ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, declarative_base
import os
Base = declarative_base()


class User(Base):  # Singular name for consistency
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname1 = Column(String)
    surname2 = Column(String)
    dni = Column(String)
    email = Column(String)
    telephone = Column(Integer)  # New column added

    # Relationships
    expenses = relationship('Expense', back_populates='user')
    incomes = relationship('Income', back_populates='user')
    savings = relationship('Saving', back_populates='user')
    accounts = relationship('Account', back_populates='user')
    investments = relationship('Investment', back_populates='user')

class Place(Base):  # Singular name for consistency
    __tablename__ = 'places'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    description = Column(String)

    # Relationships
    expenses = relationship('Expense', back_populates='place')


class ExpensesCategory(Base):  # Singular name for consistency
    __tablename__ = 'expenses_categories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    # Relationships
    expenses = relationship('Expense', back_populates='category')

class Expense(Base):  # Singular name for consistency
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    amount = Column(Float, nullable=False)  # Changed to Float for decimal amounts
    date = Column(Date, nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'))
    place_id = Column(Integer, ForeignKey('places.id'))
    category_id = Column(Integer, ForeignKey('expenses_categories.id'))

    # Relationships
    user = relationship('User', back_populates='expenses')
    place = relationship('Place', back_populates='expenses')
    category = relationship('ExpensesCategory', back_populates='expenses')

class Source(Base):  # Singular name for consistency
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    # Relationships
    incomes = relationship('Income', back_populates='source')


class CategoryIncome(Base):  # Singular name for consistency
    __tablename__ = 'categories_incomes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    # Relationships
    incomes = relationship('Income', back_populates='category')

class Income(Base):  # Singular name for consistency
    __tablename__ = 'incomes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    amount = Column(Float, nullable=False)  # Float for decimal amounts
    date = Column(Date , nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'))
    source_id = Column(Integer, ForeignKey('sources.id'))
    category_id = Column(Integer, ForeignKey('categories_incomes.id'))

    # Relationships
    user = relationship('User', back_populates='incomes')
    source = relationship('Source', back_populates='incomes')
    category = relationship('CategoryIncome', back_populates='incomes')


class Saving(Base):  # Singular name for consistency
    __tablename__ = 'savings'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    amount = Column(Float, nullable=False)  # Float for decimal amounts
    date = Column(Date, nullable=False)  # Changed to Date for consistency

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))

    # Relationships
    user = relationship('User', back_populates='savings')
    account = relationship('Account', back_populates='savings')

class Account(Base):  # Singular name for consistency
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    iban = Column(String, nullable=False)
    balance = Column(Float, nullable=False)  # Float for decimal amounts

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'))
    bank_id = Column(Integer, ForeignKey('banks.id'))

    # Relationships
    user = relationship('User', back_populates='accounts')
    bank = relationship('Bank', back_populates='accounts')
    savings = relationship('Saving', back_populates='account')
    investments = relationship('Investment', back_populates='account')

class Bank(Base):  # Singular name for consistency
    __tablename__ = 'banks'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    # Relationships
    accounts = relationship('Account', back_populates='bank')  # One-to-Many relationship with accounts

class CategoryInvestment(Base):  # Singular name for consistency
    __tablename__ = 'categories_investments'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    # Relationships
    investments = relationship('Investment', back_populates='category')


class Investment(Base):  # Singular name for consistency
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    amount = Column(Float, nullable=False)  # Float for decimal amounts
    value = Column(Float, nullable=False)  # Float for investment value
    date = Column(Date, nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    category_id = Column(Integer, ForeignKey('categories_investments.id'))

    # Relationships
    user = relationship('User', back_populates='investments')
    account = relationship('Account', back_populates='investments')
    category = relationship('CategoryInvestment', back_populates='investments')



# Create a SQLite database in memory or on disk (ensure the directory exists for disk-based DBs)
# Ensure the 'db' directory exists
os.makedirs("../db", exist_ok=True)

# Database path
DATABASE_PATH = "../db/economy.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Check if the database exists
database_exists = os.path.exists(DATABASE_PATH)

# Create an engine
engine = create_engine(DATABASE_URL, echo=True)


# Create tables only if the database does not exist
if not database_exists:
    Base.metadata.create_all(engine)
    # Create a session to interact with the database
    Session = sessionmaker(bind=engine)
    session = Session()

    # Example: Adding a User to the Database
    new_user = User(name='miguel', surname1='martin', email='mimarben@gamil.com')
    session.add(new_user)
    session.commit()

    # Example: Querying Users from the Database
    users_query_result = session.query(User).all()
    for user in users_query_result:
        print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")

    # Example: Adding an Account Linked to a User and Bank
    new_bank = Bank(name="ING", description="Tu banco no banco")
    new_account = Account(name="Cuenta Nómina", description="Cuenta para la nómina",
                        iban="ES09 1465 0100 94 1703409446", balance=1234.71, user=new_user, bank=new_bank)

    session.add(new_bank)
    session.add(new_account)
    session.commit()

    # Querying Accounts and Banks from the Database
    accounts_query_result = session.query(Account).all()
    for account in accounts_query_result:
        print(f"Account Name: {account.name}, IBAN: {account.iban}, Balance: {account.balance}")
    print("Database and tables created!")
else:
    print("Database already exists, skipping creation.")


    
