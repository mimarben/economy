# routes.py
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.user_schema import UserCreate, UserRead, UserUpdate
from services.user_service import UserService
from services.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.response_service import Response


router = Blueprint("users", __name__)
name = "users"


# Dependency Injection - Each endpoint depends only on what it needs (ISP)
def _get_create_service(db: Session) -> ICreateService:
    """Inject only create interface."""
    return UserService(db)


def _get_read_service(db: Session) -> IReadService:
    """Inject only read interface."""
    return UserService(db)


def _get_update_service(db: Session) -> IUpdateService:
    """Inject only update interface."""
    return UserService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    """Inject only delete interface."""
    return UserService(db)


@router.post("/users")
def create_user():
    """Create a new user."""
    db: Session = next(get_db())

    try:
        user_data = UserCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(user_data)
        return Response._ok_data(
            result.model_dump(),
            _("USER_CREATED"),
            201,
            name
        )
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 409, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/users/<int:user_id>")
def get_user(user_id):
    """Get a single user by ID."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        result = service.get_by_id(user_id)

        if not result:
            return Response._error(_("USER_NOT_FOUND"), _("USER_NOT_FOUND_DATABASE"), 404, name)

        return Response._ok_data(result.model_dump(), _("USER_FOUND"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/users")
def list_users():
    """Get all users."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        results = service.get_all()

        return Response._ok_data(
            [r.model_dump() for r in results],
            _("USER_LIST"),
            200,
            name
        )
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/users/<int:user_id>")
def update_user(user_id):
    """Update a user."""
    db: Session = next(get_db())

    try:
        user_data = UserUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(user_id, user_data)

        if not result:
            return Response._error(_("USER_NOT_FOUND"), _("USER_NOT_FOUND_DATABASE"), 404, name)

        return Response._ok_data(result.model_dump(), _("USER_UPDATED"), 200, name)
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 409, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/users/<int:user_id>")
def delete_user(user_id):
    """Delete a user."""
    db: Session = next(get_db())

    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(user_id)

        if not success:
            return Response._error(_("USER_NOT_FOUND"), _("USER_NOT_FOUND_DATABASE"), 404, name)

        return Response._ok_message(_("USER_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/users")
def list_users():
    db = next(get_db())
    try:
        users = db.query(User).all()
        # Convertir modelos de SQLAlchemy a Pydantic UserRead y serializar
        user_data = [UserRead.model_validate(u).model_dump() for u in users]
        if not user_data:
            return Response._error(_("USER_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(user_data, _("USERS_FOUND"), 200, name)
    except Exception as e:
        return Response._error(_("UNKNOWN_ERROR"), e.error(), 500, name)

