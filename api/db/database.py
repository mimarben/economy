import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from models import Base, User, Account, Bank
from config import Config  # Double dot moves up two levels (api/db → api → root)

DATABASE_PATH = Config.DATABASE_PATH

# Construct the database URL
# DATABASE_URL = f"sqlite:///{os.path.abspath(DATABASE_PATH)}"
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"📁 Database absolute path: {os.path.abspath(DATABASE_PATH)}")
print(f"📁 Database DATABASE_URL path: {DATABASE_URL}")
print(f"📁 Database DB_ENGINE: {Config.DB_ENGINE}")

engine = create_engine(
    DATABASE_URL, echo=True, pool_size=20, max_overflow=10, pool_timeout=60
)

# ✅ Enable foreign key constraints only for SQLite
if Config.DB_ENGINE == "sqlite":

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
        print("Database connection successful!")
    except Exception as e:
        # init_db()
        print(f"Error connecting to the database: {e}")
    finally:
        db.close()
        print("Database session closed!")


def init_db():
    # SQLITE_PATH = os.getenv("SQLITE_PATH", "db/economy.db")
    if Config.DB_ENGINE == "sqlite":
        os.makedirs("db", exist_ok=True)
        database_exists = os.path.exists(DATABASE_PATH)
    else:
        # En PostgreSQL siempre intentamos crear tablas si no existen
        database_exists = False

    # Create an engine
    engine = create_engine(DATABASE_URL, echo=True)

    if not database_exists or Config.DB_ENGINE == "postgres":
        # Create tables only if the database does not exist
        Base.metadata.create_all(engine)
        # Create a session to interact with the database
        Session = sessionmaker(bind=engine)
        session = Session()
        # Example: Adding a User to the Database
        new_user = User(
            name="name",
            surname1="surname1",
            dni="12345678Z",
            surname2="surname2",
            telephone=123456789,
            email="example@email.com",
            active=True,
        )
        session.add(new_user)
        session.commit()
        # Example: Querying Users from the Database
        users_query_result = session.query(User).all()
        for user in users_query_result:
            print(
                f"ID: {user.id}, Name: {user.name}, Email: {user.email}",
                "dni:",
                user.dni,
                "surname1:",
                user.surname1,
                "surname2:",
                user.surname2,
                "telephone:",
                user.telephone,
            )
        # Example: Adding an Account Linked to a User and Bank
        new_bank = Bank(name="ING", description="Tu banco no banco")
        new_account = Account(
            name="Cuenta Nómina",
            description="Cuenta para la nómina",
            iban="ES09 8989 0250 32 9903400006",
            balance=1234.71,
            user=new_user,
            bank=new_bank,
        )
        session.add(new_bank)
        session.add(new_account)
        session.commit()
        # Querying Accounts and Banks from the Database
        accounts_query_result = session.query(Account).all()
        for account in accounts_query_result:
            print(
                f"Account Name: {account.name}, IBAN: {account.iban}, Balance: {account.balance}"
            )
        print("Database and tables created!")
    else:
        print("Database already exists, skipping creation.")
