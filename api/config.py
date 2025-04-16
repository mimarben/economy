import os
import sys
from dotenv import load_dotenv
load_dotenv()
dbpath = os.getenv('DATABASE_PATH')
class Config:
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
    
class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = "db/economy_test.db"  # Path to translation files
    

class ProductionConfig(Config):
    DEBUG = False