"""Wiring tests for the admin role dependencies on the users router.

Without an HTTP client (no httpx in the venv), these tests walk the real
FastAPI route objects and exercise the exact dependency callables that the
app would run per request.
"""
import pytest
from fastapi import HTTPException

from routers.users.user_router import router as user_router
from services.auth.auth_dependencies import get_current_user_role

_ADMIN = "administrator"


def _route(path: str, method: str):
    # The router declares params with the Starlette int converter
    # ("/users/{user_id:int}"); normalize it for the lookup.
    normalized = path.replace("{user_id}", "{user_id:int}")
    for route in user_router.routes:
        if route.path in (path, normalized) and route.methods and method in route.methods:
            return route
    raise AssertionError(f"Route {method} {path} not found on the users router")


def _dependency_calls(route):
    """Callables wired via Depends() for a route (sub-dependencies included)."""
    return [dep.call for dep in route.dependant.dependencies]


def _role_checker(route):
    """The require_role(...)-generated checker wired into a route, if any."""
    for call in _dependency_calls(route):
        if "require_role" in getattr(call, "__qualname__", ""):
            return call
    return None


def test_list_users_wired_with_admin_role_check():
    checker = _role_checker(_route("/users", "GET"))
    assert checker is not None, "GET /users must depend on require_role(administrator)"

    # Same object the framework runs per request: admin passes, user is rejected.
    assert checker(token={"role": _ADMIN}) == {"role": _ADMIN}
    with pytest.raises(HTTPException) as exc:
        checker(token={"role": "user"})
    assert exc.value.status_code == 403


def test_create_user_wired_with_admin_role_check():
    checker = _role_checker(_route("/users", "POST"))
    assert checker is not None, "POST /users must depend on require_role(administrator)"


def test_password_reset_wired_with_admin_role_check():
    checker = _role_checker(_route("/users/{user_id}/password/reset", "POST"))
    assert checker is not None, "POST /users/{id}/password/reset must depend on require_role(administrator)"


def test_update_user_wired_with_caller_role_context():
    calls = _dependency_calls(_route("/users/{user_id}", "PATCH"))
    assert get_current_user_role in calls, (
        "PATCH /users/{id} must read the caller role to allow admin edits of other users"
    )
