"""Router for Bank endpoints following ISP - Dependency Inversion Principle."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.bank_schema import BankCreate, BankUpdate
from services.bank_service import BankService
from services.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.response_service import Response


router = Blueprint("banks", __name__)
name = "banks"


# Dependency Injection - Each endpoint depends only on what it needs (ISP)
def _get_create_service(db: Session) -> ICreateService:
    """Inject only create interface."""
    return BankService(db)


def _get_read_service(db: Session) -> IReadService:
    """Inject only read interface."""
    return BankService(db)


def _get_update_service(db: Session) -> IUpdateService:
    """Inject only update interface."""
    return BankService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    """Inject only delete interface."""
    return BankService(db)


@router.post("/banks")
def create():
    """Create a new bank."""
    db: Session = next(get_db())

    try:
        data = BankCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("BANK_CREATED"), 201, name)
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/banks/<int:id>")
def get_by_id(id):
    """Get a single bank by ID."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        result = service.get_by_id(id)

        if not result:
            return Response._error(_("BANK_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(result.model_dump(), _("BANK_FOUND"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/banks")
def list_all():
    """Get all banks."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        results = service.get_all()

        return Response._ok_data(
            [r.model_dump() for r in results],
            _("BANK_LIST"),
            200,
            name
        )
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/banks/<int:id>")
def update(id):
    """Update a bank."""
    db: Session = next(get_db())

    try:
        data = BankUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)

        if not result:
            return Response._error(_("BANK_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(result.model_dump(), _("BANK_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/banks/<int:id>")
def delete(id):
    """Delete a bank."""
    db: Session = next(get_db())

    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(id)

        if not success:
            return Response._error(_("BANK_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_message(_("BANK_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
