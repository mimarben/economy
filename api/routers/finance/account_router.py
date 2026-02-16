"""Router for Account endpoints following ISP - Dependency Inversion Principle."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.finance.account_schema import AccountCreate, AccountUpdate
from services.finance.account_service import AccountService
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.core.response_service import Response


router = Blueprint("accounts", __name__)
name = "accounts"


# Dependency Injection - Each endpoint depends only on what it needs (ISP)
def _get_create_service(db: Session) -> ICreateService:
    """Inject only create interface."""
    return AccountService(db)


def _get_read_service(db: Session) -> IReadService:
    """Inject only read interface."""
    return AccountService(db)


def _get_update_service(db: Session) -> IUpdateService:
    """Inject only update interface."""
    return AccountService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    """Inject only delete interface."""
    return AccountService(db)


@router.post("/accounts")
def create():
    """Create a new account."""
    db: Session = next(get_db())

    try:
        data = AccountCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("ACCOUNT_CREATED"), 201, name)
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/accounts/<int:id>")
def get_by_id(id):
    """Get a single account by ID."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        result = service.get_by_id(id)

        if not result:
            return Response._error(_("ACCOUNT_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(result.model_dump(), _("ACCOUNT_FOUND"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/accounts")
def list_all():
    """Get all accounts."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        results = service.get_all()

        return Response._ok_data(
            [r.model_dump() for r in results],
            _("ACCOUNT_LIST"),
            200,
            name
        )
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/accounts/<int:id>")
def update(id):
    """Update an account."""
    db: Session = next(get_db())

    try:
        data = AccountUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)

        if not result:
            return Response._error(_("ACCOUNT_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(result.model_dump(), _("ACCOUNT_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/accounts/<int:id>")
def delete(id):
    """Delete an account."""
    db: Session = next(get_db())

    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(id)

        if not success:
            return Response._error(_("ACCOUNT_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_message(_("ACCOUNT_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
