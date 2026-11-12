import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from sqlalchemy.orm import Session as ORMSession


@contextmanager
def atomic(session: ORMSession):
    """Run a block atomically regardless of the session's current state.

    `session.begin()` raises InvalidRequestError if the session already has an
    implicit transaction (autobegin from a prior read). This helper commits on
    success / rolls back on error either way.
    """
    if session.in_transaction():
        try:
            yield
            session.commit()
        except Exception:
            session.rollback()
            raise
    else:
        with session.begin():
            yield
from models import Base, User, Account, Bank
from config import Config
from .users_seed import seed_admin

DATABASE_URL = Config.DATABASE_URL

# Setup logging
from services.logs.logger_service import setup_logger
logger = setup_logger("database")

logger.info(f"Database URL: {DATABASE_URL}")
logger.info(f"Database Engine: {Config.DB_ENGINE}")

engine = create_engine(
    DATABASE_URL,
    echo=Config.DEBUG,
    # FastAPI runs sync endpoints in a threadpool of 40 threads; the pool
    # must cover them or requests queue on pool_timeout under load.
    pool_size=40,
    max_overflow=10,
    pool_timeout=60
)

# ✅ Enable foreign key constraints only for SQLite
if Config.DB_ENGINE == "sqlite":
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Provide one SQLAlchemy session per request."""
    db = SessionFactory()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Context manager for database sessions. Preferred for explicit lifecycle control."""
    db = SessionFactory()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


def init_db():
    schema_strategy = getattr(Config, "SCHEMA_INIT_STRATEGY", "create_all")

    if schema_strategy == "create_all":
        if Config.DB_ENGINE == "sqlite":
            os.makedirs("db", exist_ok=True)
            database_exists = os.path.exists(DATABASE_URL)
            if not database_exists:
                Base.metadata.create_all(engine)
                logger.info("SQLite database and tables created.")
        else:
            Base.metadata.create_all(engine)
            logger.warning("create_all strategy enabled outside SQLite; prefer Alembic for managed environments.")
    elif schema_strategy == "migrations":
        logger.info("Schema lifecycle delegated to Alembic migrations.")
    else:
        raise ValueError(f"Invalid SCHEMA_INIT_STRATEGY: {schema_strategy}")

    if getattr(Config, "SEED_DB_ON_STARTUP", False):
        with get_db_session() as db:
            seed_admin(db)
        logger.info("Seed data verification completed.")
