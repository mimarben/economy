"""Unit tests for AuthService (register / login / refresh / get_current_user).

Follows the existing suite conventions: pytest plain functions, real in-memory
SQLite, real bcrypt, no mocking. ``login``/``refresh`` need a Flask app context
because they call flask_jwt_extended token helpers.
"""
import pytest

from models import User, UserRoleEnum
from schemas.auth.auth_schema import LoginRequest, RegisterRequest
# Importing this module executes UserRead.model_rebuild(...) at its bottom, which
# resolves the `AccountCompact` forward reference. In the running app this happens
# via router imports; in isolated tests we trigger it explicitly.
import schemas.finance.account_schema  # noqa: F401
from services.auth.auth_service import AuthService
from services.core.security_service import hash_password

# DNIs below are valid under the check_dni letter algorithm (^\d{8}[A-Z]$ + letter).
_VALID_DNI = "11111111H"
_ALT_DNI = "22222222J"
_SEED_DNI = "12345678Z"
_PASSWORD = "Password1!"


def _register_payload(email="new@example.com", dni=_VALID_DNI, password=_PASSWORD):
    return RegisterRequest(
        name="Ada",
        surname1="Lovelace",
        surname2=None,
        dni=dni,
        email=email,
        telephone=None,
        password=password,
    )


def _seed_user(db_session, email="login@example.com", password=_PASSWORD, active=True):
    user = User(
        name="Test",
        surname1="User",
        dni=_SEED_DNI,
        email=email,
        active=active,
        password=hash_password(password),
        role=UserRoleEnum.USER,
    )
    db_session.add(user)
    db_session.commit()
    return user


# ───────────────────────────── register ─────────────────────────────

def test_register_success(db_session):
    created = AuthService(db_session).register(_register_payload())

    assert created.id is not None
    assert created.email == "new@example.com"
    # password must be hashed, never stored in plain text
    db_user = db_session.get(User, created.id)
    assert db_user.password != _PASSWORD
    # DB defaults applied
    assert db_user.role == UserRoleEnum.USER
    assert db_user.active is True


def test_register_rejects_duplicate_email(db_session):
    AuthService(db_session).register(_register_payload(email="dup@example.com"))

    with pytest.raises(ValueError) as exc:
        AuthService(db_session).register(
            _register_payload(email="dup@example.com", dni=_ALT_DNI)
        )
    assert "EMAIL_ALREADY_EXISTS" in str(exc.value)


def test_register_rejects_duplicate_dni(db_session):
    AuthService(db_session).register(_register_payload(email="a@example.com", dni=_VALID_DNI))

    with pytest.raises(ValueError) as exc:
        AuthService(db_session).register(_register_payload(email="b@example.com", dni=_VALID_DNI))
    assert "DNI_ALREADY_EXISTS" in str(exc.value)


# ───────────────────────────── login ─────────────────────────────

def test_login_success(db_session, app_context):
    _seed_user(db_session)
    result = AuthService(db_session).login(
        LoginRequest(email="login@example.com", password=_PASSWORD)
    )

    assert result is not None
    assert result.access_token
    assert result.refresh_token
    assert result.token_type == "Bearer"


def test_login_unknown_email_returns_none(db_session, app_context):
    result = AuthService(db_session).login(
        LoginRequest(email="nobody@example.com", password=_PASSWORD)
    )
    assert result is None


def test_login_inactive_user_returns_none(db_session, app_context):
    _seed_user(db_session, active=False)
    result = AuthService(db_session).login(
        LoginRequest(email="login@example.com", password=_PASSWORD)
    )
    assert result is None


def test_login_wrong_password_returns_none(db_session, app_context):
    _seed_user(db_session)
    result = AuthService(db_session).login(
        LoginRequest(email="login@example.com", password="WrongPass1!")
    )
    assert result is None


# ───────────────────────────── refresh ─────────────────────────────

def test_refresh_success(db_session, app_context):
    user = _seed_user(db_session)
    result = AuthService(db_session).refresh(str(user.id))

    assert result.access_token
    assert result.token_type == "Bearer"


def test_refresh_unknown_user_raises(db_session, app_context):
    with pytest.raises(ValueError) as exc:
        AuthService(db_session).refresh("99999")
    assert "USER_NOT_FOUND" in str(exc.value)


# ─────────────────────────── get_current_user ───────────────────────────

def test_get_current_user_found(db_session):
    user = _seed_user(db_session)
    result = AuthService(db_session).get_current_user(str(user.id))
    assert result is not None
    assert result.id == user.id


def test_get_current_user_not_found(db_session):
    assert AuthService(db_session).get_current_user("99999") is None
