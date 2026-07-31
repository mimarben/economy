"""Shared pytest fixtures for the Economy API test suite.

This file is ADDITIVE: existing test modules keep their own local fixtures
(pytest resolves module-level fixtures before conftest, so there is no collision).
New test modules can rely on the shared fixtures here instead of redefining them.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB


# SQLite has no native JSONB. Compile JSONB columns as JSON when building the
# in-memory schema (Base.metadata contains every model, including JSONB ones).
@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


from models import Base  # noqa: E402  (shim must register before create_all)


@pytest.fixture
def db_session():
    """Fresh in-memory SQLite session, isolated per test (recreated, not rolled back)."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def app_context():
    """Minimal Flask app context so flask_jwt_extended token helpers work.

    AuthService.login/refresh call create_access_token/create_refresh_token,
    which read ``current_app.config``. The full ``create_app`` is not used here
    because TestingConfig lacks ``PREFIX`` (needed by blueprint registration) and
    the service layer does not need routers/blueprints — only the JWT config.
    """
    from flask import Flask
    from flask_jwt_extended import JWTManager

    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "testing-jwt-secret"
    JWTManager(app)

    with app.app_context():
        yield app
