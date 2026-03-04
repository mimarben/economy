"""Authentication routes — register, login, refresh, me."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _
from flask_jwt_extended import jwt_required, get_jwt_identity

from schemas.auth.auth_schema import LoginRequest, RegisterRequest
from services.auth.auth_service import AuthService
from services.core.response_service import Response
from db.database import get_db

router = Blueprint("auth", __name__)
name = "auth"


@router.post("/auth/register")
def register():
    """Register a new user. Public endpoint."""
    db: Session = next(get_db())

    try:
        data = RegisterRequest.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service = AuthService(db)
        user = service.register(data)
        return Response._ok_data(
            user.model_dump(),
            _("USER_REGISTERED"),
            201,
            name
        )
    except ValueError as e:
        return Response._error(_("REGISTRATION_ERROR"), str(e), 409, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.post("/auth/login")
def login():
    """Authenticate user and return JWT tokens. Public endpoint."""
    db: Session = next(get_db())

    try:
        data = LoginRequest.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service = AuthService(db)
        result = service.login(data)

        if not result:
            return Response._error(
                _("AUTH_FAILED"),
                _("INVALID_CREDENTIALS"),
                401,
                name
            )

        return Response._ok_data(
            result.model_dump(),
            _("LOGIN_SUCCESS"),
            200,
            name
        )
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    """Get a new access token using a refresh token. Requires valid refresh token."""
    db: Session = next(get_db())

    try:
        current_user_id = get_jwt_identity()
        service = AuthService(db)
        result = service.refresh(current_user_id)

        return Response._ok_data(
            result.model_dump(),
            _("TOKEN_REFRESHED"),
            200,
            name
        )
    except ValueError as e:
        return Response._error(_("AUTH_ERROR"), str(e), 404, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/auth/me")
@jwt_required()
def me():
    """Get current authenticated user data. Protected endpoint."""
    db: Session = next(get_db())

    try:
        current_user_id = get_jwt_identity()
        service = AuthService(db)
        user = service.get_current_user(current_user_id)

        if not user:
            return Response._error(_("USER_NOT_FOUND"), _("USER_NOT_FOUND"), 404, name)

        return Response._ok_data(
            user.model_dump(),
            _("USER_FOUND"),
            200,
            name
        )
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
