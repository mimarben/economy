from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from utils.i18n import _

from models.core.enums import UserRoleEnum
from schemas.users.user_schema import UserCreate, UserRead, UserUpdate
from services.users.user_service import UserService
from services.core.response_service import Response
from services.auth.auth_dependencies import (
    get_current_user_id,
    get_current_user_role,
    require_role,
)
from db.database import get_db


router = APIRouter()
name = "users"

# User management (listing/creation) is reserved to administrators.
_require_admin = require_role(UserRoleEnum.ADMIN.value)


def _get_service(db: Session) -> UserService:
    """Dependency: UserService bound to the request session."""
    return UserService(db)


@router.post("/users")
def create_user(payload: UserCreate, db: Session = Depends(get_db), _admin: dict = Depends(_require_admin)):
    """Create a new user (admin only)."""
    service = _get_service(db)
    try:
        result = service.create(payload)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 409, name)
    return Response.ok_data(result.model_dump(), _("USER_CREATED"), 201, name)


@router.get("/users/{user_id:int}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Get a single user by ID (own data only)."""
    if user_id != current_user_id:
        return Response.error(_("AUTH_FORBIDDEN"), _("AUTH_FORBIDDEN"), 403, name)

    service = _get_service(db)
    result = service.get_by_id(user_id)

    if not result:
        return Response.error(_("USER_NOT_FOUND"), _("USER_NOT_FOUND_DATABASE"), 404, name)

    return Response.ok_data(result.model_dump(), _("USER_FOUND"), 200, name)


@router.get("/users")
def list_users(db: Session = Depends(get_db), _admin: dict = Depends(_require_admin)):
    """Get all users (admin only)."""
    service = _get_service(db)
    results = service.get_all()

    return Response.ok_data(
        [r.model_dump() for r in results],
        _("USER_LIST"),
        200,
        name
    )


@router.patch("/users/{user_id:int}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_role: str = Depends(get_current_user_role),
):
    """Update a user (own data, or any user as administrator)."""
    if user_id != current_user_id and current_role != UserRoleEnum.ADMIN.value:
        return Response.error(_("AUTH_FORBIDDEN"), _("AUTH_FORBIDDEN"), 403, name)

    service = _get_service(db)
    try:
        result = service.update(
            user_id,
            payload,
            current_user_id=current_user_id,
            current_role=current_role,
        )
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 409, name)

    if not result:
        return Response.error(_("USER_NOT_FOUND", id=user_id), _("USER_NOT_FOUND_DATABASE", id=user_id), 404, name)

    return Response.ok_data(result.model_dump(), _("USER_UPDATED"), 200, name)


@router.post("/users/{user_id:int}/password/reset")
def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(_require_admin),
):
    """Generate a new temporary password for a user (admin only).

    The plaintext password is returned exactly once; only its hash is stored.
    """
    service = _get_service(db)
    result = service.reset_password(user_id)

    if not result:
        return Response.error(_("USER_NOT_FOUND", id=user_id), _("USER_NOT_FOUND_DATABASE", id=user_id), 404, name)

    return Response.ok_data(result, _("USER_PASSWORD_RESET"), 200, name)


@router.delete("/users/{user_id:int}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Delete a user (own data only)."""
    if user_id != current_user_id:
        return Response.error(_("AUTH_FORBIDDEN"), _("AUTH_FORBIDDEN"), 403, name)

    service = _get_service(db)
    success = service.delete(user_id)

    if not success:
        return Response.error(_("USER_NOT_FOUND"), _("USER_NOT_FOUND_DATABASE"), 404, name)

    return Response.ok_message(_("USER_DELETED"), 204, name)
