import os
import sys
from dotenv import load_dotenv
load_dotenv()
dbpath = os.getenv('DATABASE_PATH').strip()
class Config:
    DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")
    if DB_ENGINE == "sqlite":
        SQLITE_PATH = os.getenv("SQLITE_PATH", "db/economy.db")
        DATABASE_URL = f"sqlite:///{os.path.abspath(SQLITE_PATH)}"
    else:
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        db = os.getenv("POSTGRES_DB")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
        raise ValueError("DB_ENGINE debe ser sqlite o postgres")

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    LANGUAGES = {
    'en': 'English',
    'es': 'Spanish'
    }
    # Flask-Babel settings
    BABEL_DEFAULT_LOCALE = 'en'  # Default language
    BABEL_TRANSLATION_DIRECTORIES = 'i18n'  # Path to translation files
    # DataBase
    DATABASE_PATH = dbpath  # Path to translation files

class DevelopmentConfig(Config):
    DEBUG = True
    PORT=5001
    HOST="0.0.0.0"
    PREFIX="/api"
    CORS = {
        "origins": ["http://localhost:4200"],
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = "db/economy_test.db"  # Path to translation files


class ProductionConfig(Config):
    DEBUG = False
    PORT=5000
    HOST=""
    PREFIX="/api"
