"""Router for Bank endpoints following ISP - Dependency Inversion Principle."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.finance.bank_schema import BankCreate, BankUpdate

from services.finance.bank_service import BankService
from services.logs.logger_service import setup_logger

from services.core.response_service import Response
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService

from db.database import get_db


router = Blueprint("banks", __name__)
NAME = "banks"


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
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("BANK_CREATED"), 201, NAME)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/banks/<int:id>")
def get_by_id(id):
    """Get a single bank by ID."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        result = service.get_by_id(id)

        if not result:
            return Response.error(_("BANK_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("BANK_FOUND"), 200, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in get %s by ID %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/banks")
def list_all():
    """Get all banks."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        results = service.get_all()

        return Response.ok_data(
            [r.model_dump() for r in results],
            _("BANK_LIST"),
            200,
            NAME
        )
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in list all %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.patch("/banks/<int:id>")
def update(bank_id: int):
    """Update a bank."""
    db: Session = next(get_db())

    try:
        data = BankUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(bank_id, data)

        if not result:
            return Response.error(_("BANK_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("BANK_UPDATED"), 200, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in update %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.delete("/banks/<int:id>")
def delete(bank_id: int):
    """Delete a bank."""
    db: Session = next(get_db())

    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(bank_id)

        if not success:
            return Response.error(_("BANK_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_message(_("BANK_DELETED"), 204, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in delete %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)
