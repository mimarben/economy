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
        host = os.getenv("POSTGRES_HOST")
        
        # Use localhost if not in Docker and no explicit host provided
        in_docker = os.path.exists("/.dockerenv")
        if not host or (host == "postgres" and not in_docker):
            host = "postgres" if in_docker else "localhost"
        
        port = os.getenv("POSTGRES_PORT", "5432")
        DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    else:
        raise ValueError(
            f"DB_ENGINE inválido: {DB_ENGINE}. Debe ser 'sqlite' o 'postgres'"
        )

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    LANGUAGES = {
        'en': 'English',
        'es': 'Spanish'
    }
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_TRANSLATION_DIRECTORIES = 'i18n'
    INIT_DB_ON_STARTUP = False


class DevelopmentConfig(Config):
    DEBUG = True
    PORT = 5001
    HOST = "0.0.0.0"
    PREFIX = "/api"
    JWT_SECRET_KEY = Config.JWT_SECRET_KEY or 'dev-jwt-secret-change-in-production'
    CORS = {
        "origins": ["http://localhost:4200"],
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
    INIT_DB_ON_STARTUP = True


class TestingConfig(Config):
    TESTING = True
    JWT_SECRET_KEY = 'testing-jwt-secret'    # ✅ fixed value, no env dependency


class ProductionConfig(Config):
    DEBUG = False
    PORT = 5000
    HOST = "0.0.0.0"
    PREFIX = "/api"
    CORS = {
        "origins": os.getenv("ALLOWED_ORIGINS", "").split(","),
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }

    @classmethod
    def validate(cls):
        if not cls.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in production environment")
