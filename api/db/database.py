import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from models import Base, User, Account, Bank
from config import Config

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
    else:
        database_exists = False

    if not database_exists or Config.DB_ENGINE == "postgres":
        Base.metadata.create_all(engine)
        logger.info("Database and tables created!")
    else:
        logger.info("Database already exists, skipping creation.")
