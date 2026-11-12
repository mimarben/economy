"""Router for Bank endpoints following ISP - Dependency Inversion Principle."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.finance.bank_schema import BankBase, BankCreate, BankUpdate

from schemas.core.export_schema import export_schema

from services.finance.bank_service import BankService
from services.logs.logger_service import setup_logger

from services.core.response_service import Response

from db.database import get_db


router = APIRouter()
NAME = "banks"


def _get_service(db: Session) -> BankService:
    """Dependency: service bound to the request session."""
    return BankService(db)


@router.post("/banks")
def create(payload: BankCreate, db: Session = Depends(get_db)):
    """Create a new bank."""
    try:
        data = BankCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("BANK_CREATED"), 201, NAME)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/banks/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    """Get a single bank by ID."""
    try:
        service = _get_service(db)
        result = service.get_by_id(id)

        if not result:
            return Response.error(_("BANK_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("BANK_FOUND"), 200, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in get %s by ID %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/banks")
def list_all(db: Session = Depends(get_db)):
    """Get all banks."""
    try:
        service = _get_service(db)
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


@router.patch("/banks/{id:int}")
def update(id: int, payload: BankUpdate, db: Session = Depends(get_db)):
    """Update a bank."""
    try:
        data = BankUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service = _get_service(db)
        result = service.update(id, data)

        if not result:
            return Response.error(_("BANK_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("BANK_UPDATED"), 200, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in update %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.delete("/banks/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    """Delete a bank."""
    try:
        service = _get_service(db)
        success = service.delete(id)

        if not success:
            return Response.error(_("BANK_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_message(_("BANK_DELETED"), 204, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in delete %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/meta/bank")
def get_meta():
    return export_schema(BankBase)
