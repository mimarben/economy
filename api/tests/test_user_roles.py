"""Unit tests for UserService role guards and password reset (admin flow)."""
import re

import pytest

from models import User, UserRoleEnum
import schemas.finance.account_schema  # noqa: F401  (resolve UserRead forward refs)
from schemas.users.user_schema import UserUpdate
from services.core.security_service import hash_password, verify_password
from services.users.user_service import UserService

# Valid DNI check letters (^\d{8}[A-Z]$ + letter algorithm).
_ADMIN_DNI = "11111111H"
_USER_DNI = "22222222J"
_SECOND_ADMIN_DNI = "33333333P"
_THIRD_DNI = "44444444A"
_PASSWORD = "Password1!"

_ADMIN_ROLE = UserRoleEnum.ADMIN.value


def _seed_user(db_session, email, role=UserRoleEnum.USER, active=True, dni=_USER_DNI):
    user = User(
        name="Test",
        surname1="User",
        dni=dni,
        email=email,
        active=active,
        password=hash_password(_PASSWORD),
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    return user


# ───────────────────────── role guards on update ─────────────────────────

def test_non_admin_cannot_change_own_role(db_session):
    user = _seed_user(db_session, "user@example.com", role=UserRoleEnum.USER)

    payload = UserUpdate(role=UserRoleEnum.ADMIN)
    with pytest.raises(ValueError) as exc:
        UserService(db_session).update(
            user.id, payload, current_user_id=user.id, current_role=UserRoleEnum.USER.value
        )
    assert "ROLE_CHANGE_FORBIDDEN" in str(exc.value)


def test_non_admin_can_update_own_data_keeping_role(db_session):
    user = _seed_user(db_session, "user@example.com", role=UserRoleEnum.USER)

    payload = UserUpdate(telephone=600000000, role=UserRoleEnum.USER)
    result = UserService(db_session).update(
        user.id, payload, current_user_id=user.id, current_role=UserRoleEnum.USER.value
    )

    assert result is not None
    assert result.telephone == 600000000
    assert result.role == UserRoleEnum.USER


def test_admin_can_update_another_user_and_change_role(db_session):
    _seed_user(db_session, "admin@example.com", role=UserRoleEnum.ADMIN, dni=_ADMIN_DNI)
    user = _seed_user(db_session, "user@example.com", role=UserRoleEnum.USER)

    payload = UserUpdate(role=UserRoleEnum.ADMIN, active=True)
    result = UserService(db_session).update(
        user.id, payload, current_user_id=1, current_role=_ADMIN_ROLE
    )

    assert result is not None
    assert result.role == UserRoleEnum.ADMIN


def test_admin_cannot_change_own_role(db_session):
    admin = _seed_user(db_session, "admin@example.com", role=UserRoleEnum.ADMIN, dni=_ADMIN_DNI)

    payload = UserUpdate(role=UserRoleEnum.USER)
    with pytest.raises(ValueError) as exc:
        UserService(db_session).update(
            admin.id, payload, current_user_id=admin.id, current_role=_ADMIN_ROLE
        )
    assert "OWN_ROLE_CHANGE_FORBIDDEN" in str(exc.value)


def test_last_admin_cannot_be_deactivated(db_session):
    admin = _seed_user(db_session, "admin@example.com", role=UserRoleEnum.ADMIN, dni=_ADMIN_DNI)

    payload = UserUpdate(active=False)
    with pytest.raises(ValueError) as exc:
        UserService(db_session).update(
            admin.id, payload, current_user_id=admin.id, current_role=_ADMIN_ROLE
        )
    assert "LAST_ADMIN_PROTECTED" in str(exc.value)


def test_second_admin_can_be_demoted(db_session):
    _seed_user(db_session, "admin1@example.com", role=UserRoleEnum.ADMIN, dni=_ADMIN_DNI)
    admin2 = _seed_user(
        db_session, "admin2@example.com", role=UserRoleEnum.ADMIN, dni=_SECOND_ADMIN_DNI
    )

    payload = UserUpdate(role=UserRoleEnum.USER)
    result = UserService(db_session).update(
        admin2.id, payload, current_user_id=1, current_role=_ADMIN_ROLE
    )

    assert result is not None
    assert result.role == UserRoleEnum.USER


def test_update_without_caller_context_keeps_previous_behaviour(db_session):
    """Internal calls without token context still update (backwards compatible)."""
    user = _seed_user(db_session, "user@example.com", role=UserRoleEnum.USER)

    payload = UserUpdate(role=UserRoleEnum.ADMIN)
    result = UserService(db_session).update(user.id, payload)

    assert result is not None
    assert result.role == UserRoleEnum.ADMIN


# ───────────────────────── password reset ─────────────────────────

def test_reset_password_returns_policy_compliant_password(db_session):
    user = _seed_user(db_session, "user@example.com")

    result = UserService(db_session).reset_password(user.id)

    temporary = result["temporary_password"]
    assert result["user"].id == user.id
    # Policy: >=8 chars with upper, lower, digit and symbol (check_password).
    assert len(temporary) >= 8
    assert re.search(r"[A-Z]", temporary)
    assert re.search(r"[a-z]", temporary)
    assert re.search(r"\d", temporary)
    assert re.search(r"[^\w\s]", temporary)

    # Only the hash is persisted and it verifies against the plaintext.
    db_user = db_session.get(User, user.id)
    assert db_user.password != temporary
    assert verify_password(temporary, db_user.password)


def test_reset_password_generates_different_values_each_time(db_session):
    user = _seed_user(db_session, "user@example.com")
    service = UserService(db_session)

    first = service.reset_password(user.id)["temporary_password"]
    second = service.reset_password(user.id)["temporary_password"]

    assert first != second


def test_reset_password_unknown_user_returns_none(db_session):
    assert UserService(db_session).reset_password(99999) is None
