import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_ENGINE = os.getenv("DB_ENGINE")
    if DB_ENGINE == "sqlite":
        DATABASE_PATH = os.getenv("DATABASE_PATH")
        DATABASE_URL = f"sqlite:///{os.path.abspath(DATABASE_PATH)}"
    elif DB_ENGINE == "postgres":
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        db = os.getenv("POSTGRES_DB")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    else:
        raise ValueError(
            f"DB_ENGINE inválido: {DB_ENGINE}. Debe ser 'sqlite' o 'postgres'"
        )

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    LANGUAGES = {
        'en': 'English',
        'es': 'Spanish'
    }
    # Flask-Babel settings
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_TRANSLATION_DIRECTORIES = 'i18n'


class DevelopmentConfig(Config):
    DEBUG = True
    PORT = 5001
    HOST = "0.0.0.0"
    PREFIX = "/api"
    SECRET_KEY = Config.SECRET_KEY or 'dev-secret-key-change-in-production'
    CORS = {
        "origins": ["http://localhost:4200"],
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'testing-secret-key'


class ProductionConfig(Config):
    DEBUG = False
    PORT = 5000
    HOST = ""
    PREFIX = "/api"

    @classmethod
    def _validate(cls):
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production environment")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validate()
