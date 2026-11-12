"""Authentication routes — register, login, refresh, me."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.auth.auth_schema import LoginRequest, RegisterRequest
from services.auth.auth_service import AuthService
from services.auth.auth_dependencies import require_access_token, require_refresh_token
from services.auth.rate_limiter import login_rate_limiter
from services.auth.token_store import revoked_tokens
from services.core.response_service import Response
from db.database import get_db

router = APIRouter()
name = "auth"


@router.post("/auth/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user. Public endpoint."""
    try:
        data = RegisterRequest.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service = AuthService(db)
        user = service.register(data)
        return Response.ok_data(
            user.model_dump(),
            _("USER_REGISTERED"),
            201,
            name
        )
    except ValueError as e:
        return Response.error(_("REGISTRATION_ERROR"), str(e), 409, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.post("/auth/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens. Public endpoint, rate limited."""
    try:
        data = LoginRequest.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{data.email}"
    if login_rate_limiter.is_blocked(rate_key):
        return Response.error(_("AUTH_FAILED"), _("AUTH_RATE_LIMITED"), 429, name)

    try:
        service = AuthService(db)
        result = service.login(data)

        if not result:
            login_rate_limiter.register_failure(rate_key)
            return Response.error(
                _("AUTH_FAILED"),
                _("INVALID_CREDENTIALS"),
                401,
                name
            )

        login_rate_limiter.reset(rate_key)
        return Response.ok_data(
            result.model_dump(),
            _("LOGIN_SUCCESS"),
            200,
            name
        )
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.post("/auth/refresh")
def refresh(
    token: dict = Depends(require_refresh_token),
    db: Session = Depends(get_db),
):
    """Get a new access token using a refresh token. Requires valid refresh token."""
    try:
        current_user_id = token["sub"]
        service = AuthService(db)
        result = service.refresh(current_user_id)

        return Response.ok_data(
            result.model_dump(),
            _("TOKEN_REFRESHED"),
            200,
            name
        )
    except ValueError as e:
        return Response.error(_("AUTH_ERROR"), str(e), 404, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.post("/auth/logout")
def logout(
    token: dict = Depends(require_refresh_token),
):
    """Revoke the presented refresh token (and its access sibling via JTI).

    The token stays blocked until its original expiry; logout is stateless
    beyond the in-memory revocation store.
    """
    revoked_tokens.revoke(token.get("jti", ""), token.get("exp", 0))
    return Response.ok_message(_("LOGOUT_SUCCESS"), 200, name)


@router.get("/auth/me")
def me(
    token: dict = Depends(require_access_token),
    db: Session = Depends(get_db),
):
    """Get current authenticated user data. Protected endpoint."""
    try:
        current_user_id = token["sub"]
        service = AuthService(db)
        user = service.get_current_user(current_user_id)

        if not user:
            return Response.error(_("USER_NOT_FOUND"), _("USER_NOT_FOUND"), 404, name)

        return Response.ok_data(
            user.model_dump(),
            _("USER_FOUND"),
            200,
            name
        )
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)
