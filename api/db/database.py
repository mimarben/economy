import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
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
    pool_size=20,
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


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Generator for database sessions. Used with next() in routers."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Context manager for database sessions. Preferred for explicit lifecycle control."""
    db = SessionLocal()
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
    if Config.DB_ENGINE == "sqlite":
        os.makedirs("db", exist_ok=True)
        database_exists = os.path.exists(DATABASE_URL)
        if not database_exists:
            Base.metadata.create_all(engine)
            logger.info("SQLite database and tables created.")
    else:
        database_exists = True

    if Config.DB_ENGINE == "sqlite" and not database_exists:
        with get_db_session() as db:
            seed_admin(db)
        logger.info("Seed data created for SQLite.")
    elif Config.DB_ENGINE == "postgres":
        logger.info("Postgres detected: schema lifecycle managed by Alembic migrations.")
        with get_db_session() as db:
            seed_admin(db)
        logger.info("Seed data verified for Postgres.")
    else:
        logger.info("Database already exists, skipping creation.")
